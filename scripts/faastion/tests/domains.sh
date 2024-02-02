#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/../shared.sh

# Function to run the workload
function run {
    nrun=$1

    # Start Graalvisor and capture execution time information
    start_svm $ndomains 2>&1 | tee logs/lambda-$nrun.log | grep -E "Execution time" > logs/filtered_lambda-$nrun.log &

    # Register Java native applications in Graalvisor
    for i in $(seq $ndomains)
    do
        gv_java_native_hw_n $i 2>&1 > /dev/null
    done
    
    warmup $ndomains
    
    # Execute the workload for each domain
    for i in $(seq $workload)
    do
        (            
            for j in $(seq $ndomains)
            do
                # Send requests to Graalvisor for each application
                curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d $(cat /tmp/payload$j.post)  | jq -r '.["process time (us)"] // empty' >> logs/$approach-$j-$nrun.log &
            done
            
            # Wait for all background processes to finish
            wait
        )
    done

    # Kill Graalvisor
    pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
    kill $pid
}

# Start
if [ "$#" -ne 3 ]; then
    echo "Syntax: <approach> <# of tests> <# of domains>"
    echo "- approach=<isolate|process|faastion>"
else
    approach=$1
    workload=$2
    ndomains=$3
fi

# Setting a sandbox if not already set.
if [ "$approach" == "faastion" ]; then
    export SANDBOX=isolate
else
    export SANDBOX=$approach
fi

# Cleanup previous logs directory
if [ -d "logs" ]; then
    rm -rf "logs"
fi
mkdir -p logs

mkdir -p results

# Run 5 times to calculate average
for i in $(seq 5)
do
    run $i
done

# Generate graphs using Python script
python3 domains.py -d $ndomains -a $approach -w $workload
