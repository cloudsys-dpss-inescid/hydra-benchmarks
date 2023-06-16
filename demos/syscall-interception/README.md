# Syscall interception demos

These demos aim to benchmark the execution times of intercepting system calls:
- strace (intercept all system calls)
- seccomp (intercept all system calls except futex)
- seccomp_allow_rw (intercept all system calls except futex, read, write, and other read write variations)
- seccomp_fs (intercept file-system system calls---ie. open and close)
- seccomp_net (intercept network system calls---ie. socket and close)

This demo aims to benchmark the execution times without intercepting system calls:
- native

## Running the demos

Each demo is placed in a separate directory with a `run.sh` script that invokes the demo.
```sh
$ cd demo/directory/you/wish/to/execute
$ ./run.sh iter_count
```

If you wish to run all demos at once, use the `run_all.sh` script:
```sh
$ ./run_all.sh iter_count
```

## Plotting the results

Each demo places the results in the appropriate `.log` files. The `plot.py` script can be used to discover logs and render plots.
```sh
$ ./plot.py                            # will discover all logs and plot those demos
$ ./plot.py demo_dir1 demo_dir2        # will plot only chosen demos
```
