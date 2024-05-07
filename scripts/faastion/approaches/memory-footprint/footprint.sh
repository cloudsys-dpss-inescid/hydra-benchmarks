#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/../../shared.sh

function log_resources {
    PID=$1
    OFILE_RSS=$2/lambda-$3-$4.rss

    rm $OFILE_RSS &> /dev/null
        while kill -0 $PID &> /dev/null; do
                # The idea for memory is that we traverse the entire pid subprocess tree
                # and memory memory utilization. We sum all individual memory and return.
                s_mem=0
                for p in $(pstree -p $PID | grep -o '([0-9]\+)' | grep -o '[0-9]\+')
                do
                    p_mem=$(ps -q $p -o rss=)
                    s_mem=$((s_mem + p_mem))
                done
                echo $s_mem >> $OFILE_RSS
                sleep .050
        done
}

# Function to run the workload
function run {
    requests=$1
    run=$2

    # Start Graalvisor and capture execution time information
    start_svm &> logs/$app/$approach/lambda-$requests-$run.log &
    PID=$(echo -n "$!")

    # Log Resources (memory and CPU)
    log_resources $PID results/$app/$approach $requests $run &

    # Register application
    $app
    
    wrk -t$requests -c$requests -d1s -s native.lua http://127.0.0.1:8081

    # Kill Graalvisor
    pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
    kill $pid
}

# Start
if [ "$#" -ne 2 ]; then
    echo "Syntax: <approach> <app>"
    echo "- approach=<isolate|process|faastion>"
    echo "- app=<gv_java_native_matrix|gv_java_native_factors|...>"
    exit 1
else
    approach=$1
    app=$2
fi

# Setting a sandbox if not already set.
if [ "$approach" == "faastion" ]; then
    export SANDBOX=isolate
else
    export SANDBOX=$approach
fi

mkdir -p results/$app/$approach
mkdir -p logs/$app/$approach

nrequests=(1 3 5 8 11 14)

for n in "${nrequests[@]}"; do
    for i in $(seq 50); do
        run $n $i
    done
done
