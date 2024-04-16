#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/../../shared.sh

function log_rss {
    PID=$1
    OFILE=$2
    rm $OFILE &> /dev/null
        while kill -0 $PID &> /dev/null; do
                ps -q $PID -o rss= >> $OFILE
                sleep .5
        done
}

function log_resources {
    PID=$1
    OFILE_RSS=$2/lambda-$3.rss

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
                sleep .100
        done
}

# Function to run the workload
function run {
    run=$1

    # Start Graalvisor and capture execution time information
    start_svm &> logs/$approach/lambda-$run.log &
    PID=$(echo -n "$!")

    # Log Resources (memory and CPU)
    log_resources $PID results/$approach $run &

    # Register Java native applications in Graalvisor
    for i in $(seq 14)
    do
        gv_java_native_hw_n $i > /dev/null
    done
    
    wrk -t14 -c14 -d1s -s native.lua http://127.0.0.1:8081

    # Kill Graalvisor
    pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
    kill $pid
}

# Start
if [ "$#" -ne 1 ]; then
    echo "Syntax: <approach>"
    echo "- approach=<isolate|process|faastion>"
    exit 1
else
    approach=$1
fi

# Setting a sandbox if not already set.
if [ "$approach" == "faastion" ]; then
    export SANDBOX=isolate
else
    export SANDBOX=$approach
fi

mkdir -p results/$approach
mkdir -p logs/$approach

for i in $(seq 100); do
    run $i
done
