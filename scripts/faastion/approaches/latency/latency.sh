#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/../../shared.sh


function benchmark {
    wrk -t$requests -c$requests -d1s -s native.lua http://127.0.0.1:8081
}

function capture {
    # Execute wrk and capture the output
    output=$(benchmark)

    # Extract values using awk and redirect them to specific files
    latency=$(echo "$output" | awk '/Latency/{print $2}')

    echo $latency >> logs/$app/$approach/latency-$requests.log
}

# Function to run the workload
function run {
    requests=$1
    run=$2

    # Start Graalvisor and capture execution time information
    start_svm &> logs/$app/graalvisor/lambda-$requests-$run.log &
    
    # Register application
    $app
    
    # Uncomment for cold-start measures
    warmup 14

    capture
    #benchmark

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

if [ -d "logs/$approach" ]; then
    rm -r logs/$app/$approach/
fi

mkdir -p results/$app
mkdir -p logs/$app/$approach
mkdir -p logs/$app/graalvisor

nrequests=(1 3 5 8 11 14)

for n in "${nrequests[@]}"; do
    for i in $(seq 50); do
        run $n $i
    done
done
