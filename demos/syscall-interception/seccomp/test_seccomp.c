#include <stdio.h>
#include <stdlib.h>
#include "seccomp.h"

int main(int argc, char *argv[]) {
    if (argc <= 1) {
        fprintf(stderr, "Usage: %s command [args]\n", argv[0]);
        exit(1);
    }

    char *pathname = get_pathname(argv[1]);
    if (pathname == NULL) {
        fprintf(stderr, "%s: command not found\n", argv[1]);
        exit(1);
    }

    seccomp_init();

    int child;
    if ((child = fork()) == 0)
        exec(pathname, argv+1);
    else
        intercept_syscalls(child);

    return 0;
}