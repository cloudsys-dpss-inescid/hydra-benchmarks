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

# Function to run the workload
function run {
    run=$1

    # Start Graalvisor and capture execution time information
    start_svm &> logs/$approach/lambda-$run.log &
    PID=$(echo -n "$!")

    # Log memory.
    log_rss $PID results/$approach/lambda-$run.rss &

    # Register Java native application in Graalvisor
    gv_java_native_hw_n 1 > /dev/null

    wrk -t1 -c1 -d1s -s native.lua http://127.0.0.1:8081

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
