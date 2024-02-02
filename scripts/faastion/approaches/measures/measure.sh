#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/../../shared.sh

# Start
if [ "$#" -ne 2 ]; then
    echo "Syntax: <approach> <# of tests>"
    echo "- approach=<isolate|process|faastion>"
else
    approach=$1
    workload=$2
fi

# Setting a sandbox if not already set.
if [ "$approach" == "faastion" ]; then
    export SANDBOX=isolate
else
    export SANDBOX=$approach
fi

mkdir -p results

start_svm 1 | grep -E "sandbox time " | awk '{print $4}' > results/$approach-sb.log &

gv_java_native_hw_n 1

for i in $(seq $workload)
do
    curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d "$(cat /tmp/payload1.post)" | jq -r '.["process time (us)"] // empty' >> results/$approach-gv.log
done

# Kill graalvisor
pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
kill $pid
