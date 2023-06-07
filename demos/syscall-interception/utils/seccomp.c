#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <stddef.h>
#include <signal.h>
#include <semaphore.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <sys/ioctl.h>
#include <sys/ptrace.h>
#include <sys/syscall.h>
#include <linux/seccomp.h>
#include <linux/filter.h>
#include <linux/audit.h>
#include "seccomp.h"

#define FD_SEM "/fd_semaphore"
#define EXEC_SEM "/exec_semaphore"

#define FILE_SIZE 256

sem_t *fd_sem, *exec_sem;
char pathname[FILE_SIZE];

// Prototypes

void sigchld_handler(int signum);
int install_notify_filter();
void sendfd();
int recvfd(pid_t pid);
void handle_notifications(int nfd);

// Definitions

int is_reg_file(const char *file) {
    static struct stat sb;
    return stat(file, &sb) == 0 && S_ISREG(sb.st_mode);
}

char *_get_pathname(char name[], char *dir) {
    if (dir == NULL)
        return NULL;
    snprintf(pathname, FILE_SIZE-1, "%s/%s", dir, name);
    return is_reg_file(pathname) ? pathname : _get_pathname(name, strtok(NULL, ":"));
}

char *get_pathname(char name[]) {
    char *path = getenv("PATH");
    if (is_reg_file(name)) {
        strncpy(pathname, name, FILE_SIZE-1);
        return pathname;
    }
    else if (path == NULL || strlen(path) <= 0)
        return NULL;
    else
        return _get_pathname(name, strtok(path, ":"));
}

void seccomp_init() {
    struct sigaction sigact;
    sigemptyset(&sigact.sa_mask);
    sigact.sa_flags = 0;
    sigact.sa_handler = sigchld_handler;
    sigaction(SIGCHLD, &sigact, NULL);

    sem_unlink(FD_SEM);
    sem_unlink(EXEC_SEM);
    fd_sem = sem_open(FD_SEM, O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, 0);
    exec_sem = sem_open(EXEC_SEM, O_CREAT | O_RDWR, S_IRUSR | S_IWUSR, 0);
}

int exec(char pahtname[], char *argv[]) {
    install_notify_filter();
    sendfd();
    execv(pathname, argv);
    return 0;
}

int intercept_syscalls(pid_t pid) {
    int nfd = recvfd(pid);
    handle_notifications(nfd);
    return 0;
}

int install_notify_filter() {
    struct sock_filter filter[] = {
        BPF_STMT(BPF_LD + BPF_W + BPF_ABS, (offsetof(struct seccomp_data, arch))),
        BPF_JUMP(BPF_JMP + BPF_JEQ + BPF_K, AUDIT_ARCH_X86_64, 1, 0),
        BPF_STMT(BPF_RET + BPF_K, SECCOMP_RET_KILL),

        BPF_STMT(BPF_LD + BPF_W + BPF_ABS, (offsetof(struct seccomp_data, nr))),

        BPF_JUMP(BPF_JMP + BPF_JEQ + BPF_K, __NR_futex, 0, 1),
        BPF_STMT(BPF_RET + BPF_K, SECCOMP_RET_ALLOW),

        BPF_JUMP(BPF_JMP + BPF_JEQ + BPF_K, __NR_openat, 0, 1),
        BPF_STMT(BPF_RET + BPF_K, SECCOMP_RET_ALLOW),

        BPF_STMT(BPF_RET + BPF_K, SECCOMP_RET_USER_NOTIF),
    };
    struct sock_fprog prog = {
        .len = (unsigned short)(sizeof(filter) / sizeof(filter[0])),
        .filter = filter,
    };

    if (prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0)) {
        perror("prctl(NO_NEW_PRIVS)");
        return -1;
    }
    int rc = syscall(SYS_seccomp, SECCOMP_SET_MODE_FILTER, SECCOMP_FILTER_FLAG_NEW_LISTENER, &prog);
    if (rc < 0) {
        perror("seccomp(SECCOMP_SET_MODE_FILTER)");
        return -1;
    }
    else {
        return rc;
    }
}

void sigchld_handler(int signum) {
    exit(0);
}

void sendfd() {
    sem_post(fd_sem);
    sem_wait(exec_sem);
}

int recvfd(pid_t pid) {
    int pidfd, fd;
    sem_wait(fd_sem);
    pidfd = syscall(__NR_pidfd_open, pid, 0);
    fd = syscall(__NR_pidfd_getfd, pidfd, 3, 0);
    sem_post(exec_sem);
    return fd;
}

void handle_notifications(int nfd) {
    struct seccomp_notif_sizes sizes;
    if (syscall(SYS_seccomp, SECCOMP_GET_NOTIF_SIZES, 0, &sizes) < 0) {
        perror("seccomp(SECCOMP_GET_NOTIF_SIZES)");
        return;
    }

    struct seccomp_notif *req = (struct seccomp_notif*)malloc(sizes.seccomp_notif);
    struct seccomp_notif_resp *resp = (struct seccomp_notif_resp*)malloc(sizes.seccomp_notif_resp);

    while (1) {
        // Receive notification
        memset(req, 0, sizes.seccomp_notif);
        memset(resp, 0, sizes.seccomp_notif_resp);
        if (ioctl(nfd, SECCOMP_IOCTL_NOTIF_RECV, req) == -1) {
            perror("ioctl(SECCOMP_IOCTL_NOTIF_RECV)");
            continue;
        }

        // Print notification
        printf("Received notifaction id [%lld], from tid: %d, syscall nr: %d\n", req->id, req->pid, req->data.nr);

        // Validate notification
        if (ioctl(nfd, SECCOMP_IOCTL_NOTIF_ID_VALID, &req->id) == -1 ) {
            perror("ioctl(SECCOMP_IOCTL_NOTIF_ID_VALID)");
            continue;
        }

        // Send response
        resp->id = req->id;
        resp->flags = SECCOMP_USER_NOTIF_FLAG_CONTINUE;
        if (ioctl(nfd, SECCOMP_IOCTL_NOTIF_SEND, resp) == -1) {
            perror("ioctl(SECCOMP_IOCTL_NOTIF_SEND)");
            continue;
        }
    }
}

