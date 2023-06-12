#include <stdio.h>
#include <stdlib.h>
#include "seccomp.h"

int main(int argc, char *argv[]) {
    if (argc <= 2) {
        fprintf(stderr, "Usage: %s mode command [args]\n", argv[0]);
        exit(1);
    }

    int mode = get_seccomp_mode(argv[1]);
    if (mode < 0) {
        fprintf(stderr, "%s: invalid mode\n", argv[1]);
        exit(1);
    }

    char *pathname = get_pathname(argv[2]);
    if (pathname == NULL) {
        fprintf(stderr, "%s: command not found\n", argv[2]);
        exit(1);
    }

    seccomp_init();

    int child;
    if ((child = fork()) == 0)
        exec(pathname, argv+2, mode);
    else
        intercept_syscalls(child);

    return 0;
}