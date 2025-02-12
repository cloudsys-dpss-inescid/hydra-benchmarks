#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/shared.sh
source $(DIR)/benchmarks.sh

if [ "$#" -ne 4 ]; then
    echo "Syntax: <backend> <app> <mode> <# of tests or concurrency level>"
    echo "Available backends: graalhost (native)."
    echo "Available apps: gh_java_http"
    echo "Available modes: test benchmark. Test will perform a number of requests. Benchmark will use apache bench with the desired concurrency level."
    echo "Example: benchmark-graalhost.sh graalhost gh_java_http test 1"
    echo "Available environment variables: "
    echo "- ITERATIONS=<number> - number of iterations the workload is ran. Defaults to 1;"
    echo "- WMULTIPLIER=<number> - workload multiplier to scale up or down the length of the benchmark (only used in benchmark mode). Defaults to 256;"
    echo "- CGROUP=<name> - name of the cgroup to use. A directory with that name will be created under /sys/fs/cgroup. Defaults to empty which leads to no CGROUP being used;"
    echo "- CGROUP_CPU_QUOTA=<number> - CPU quota for a 100ms period. A quota 100000 means using a full core. Only used if CGROUP is set. Defaults to 100000 (full core)."
    echo "- PIN_CORE=<boolean> - if true, will pin the process to core 0. Defaults to false;"
    echo "- DISABLE_TURBO=<boolean> - if true, will disable turbo boost. Defaults to false;"
    echo "- EXPERIMENT=<tag> - if set, will copy result logs into a dedicated experiment directory. Defaults to unset;"
    exit 1
else
    backend=$1
    app=$2
    mode=$3
    workload=$4
fi

function benchmark {
    if [ -z "$WMULTIPLIER" ]; then
        WMULTIPLIER=256
    fi

    printf "Running ab (check $TDIR/ab.log).\n"
    ab -c $workload -n $((workload * WMULTIPLIER)) http://$IP:$APP_PORT/ &> $TDIR/ab.log
}

function test {
    printf "Sending $workload requests:\n"
    for i in $(seq 1 $workload)
    do
        request $IP:$APP_PORT/$APP_PATH
    done
}

function run {
    # Setting up environment.
    echo "Waiting for $backend..." | tee $TDIR/backend.log
    sbs=$(date +%s%N)
    IP=127.0.0.1
    start_graalhost &>> $TDIR/backend.log &

    # Let the graalhost start.
    wait_port $IP $GRAALHOST_PORT

    # Measure how long it took to accept connections.
    sbt=$((($(date +%s%N) - $sbs)/1000))
    echo "Waiting for $backend... done (took $sbt us)." | tee -a $TDIR/backend.log

    # Get PID of graalhost.
    # Note: wait until graalhost.pid is filled.
    while [ ! -f $TDIR/graalhost.pid ]; do sleep 0.01; done
    PID=$(cat $TDIR/graalhost.pid)

    # Log Resources (memory and CPU)
    log_resources $PID $TDIR &

    # Prepares the local resources (cgroups, core pinning, turbo boost).
    prepare_resources

    # Load function into runtime and prepare payload.
    $app

    # Run test/benchmark.
    $mode 2>&1 | tee -a $TDIR/app.log

    # Allow time for final collection of resource utilization.
    sleep 1

    # Teardown the graalhost.
    stop_graalhost &>> $TDIR/backend.log
    wait

    # Teardown local resource changes (delete cgroups, enable turbo boost).
    teardown_resources

    # Saving logs.
    backup_results
}

check_permissions

echo "$(tput bold)Running graalhost environment=$backend; app=$app; mode=$mode; workload=$workload:$(tput sgr0)"

# Preparing working directory
echo "Removing $TDIR and $ADIR"
rm -rf $TDIR
rm -rf $ADIR
mkdir -p $TDIR
mkdir -p $ADIR

for iter in $(seq 1 $ITERATIONS)
do
    run
done
