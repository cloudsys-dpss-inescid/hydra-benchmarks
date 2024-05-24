#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

GRAALVISOR_HOME=$ARGO_HOME/graalvisor
BENCHMARKS_HOME=$ARGO_HOME/benchmarks
JAVA_BENCHMARKS=$BENCHMARKS_HOME/src/java

LOGS_HOME=$(DIR)/logs

GREEN='\033[0;32m'
NC='\033[0m' # No Color

function gv_java_native_factors {
    APP_LANG=java
    APP_NAME=gv-native-factorization
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libfactors.so
    APP_MAIN=com.jni.Factorization
    # Register the native application in GraalVM
    curl -s -X POST 127.0.0.1:8080/register?name=factors\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"factors","async":"false","cached":"true","arguments":""}' > /tmp/payload.post
}

function gv_java_native_matrix {
    APP_LANG=java
    APP_NAME=gv-native-matrixmul
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libmatrixmul.so
    APP_MAIN=com.jni.MatrixMultiplication
    # Register the native application in GraalVM
    curl -s -X POST 127.0.0.1:8080/register?name=matrixmul\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"matrixmul","async":"false","cached":"true","arguments":""}' > /tmp/payload.post
}

function compile_jni_benchmarks {
    for benchmark in gv-native-factorization #gv-native-hw-1 gv-native-matrixmul gv-file-hashing gv-httprequest gv-sleep #gv-classify gv-video-processing
    do
        cd "$JAVA_BENCHMARKS/$benchmark"
        ./build_script.sh
        cd -
    done
}

function compile_benchmarks {
    for benchmark in gv-native-factorization #gv-native-hw-1 gv-native-matrixmul
    do
        cd "$JAVA_BENCHMARKS/$benchmark"
        ./build_script_proc_iso.sh
        cd -
    done
}

function start_svm {
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    export lambda_port="8080"
    export LD_LIBRARY_PATH=$GRAALVISOR_HOME/build/libs:$LD_LIBRARY_PATH
    export LD_PRELOAD=$GRAALVISOR_HOME/build/libs/libpreload.so
    # Start Graalvisor
    $GRAALVISOR_HOME/build/native-image/polyglot-proxy &
    wait
    unset LD_PRELOAD
}

function log_resources {
    PID=$1
    OFILE_RSS=/tmp/$approach/footprint-$workload.csv

    rm $OFILE_RSS &> /dev/null
        while kill -0 $PID &> /dev/null; do
                # The idea for memory is that we traverse the entire pid subprocess tree
                # and memory memory utilization. We sum all individual memory and return.
                s_mem=0
                timestamp=$(date -u +"%s%3N")
                for p in $(pstree -p $PID | grep -o '([0-9]\+)' | grep -o '[0-9]\+')
                do
                    p_mem=$(ps -q $p -o rss=)
                    s_mem=$((s_mem + p_mem))
                done
                echo "$s_mem,$timestamp" >> $OFILE_RSS
                sleep .100
        done
}

function benchmark {
    #wrk -t$workload -c$workload -d1s -s native.lua http://127.0.0.1:8080
    wrk -t4 -c4 -d1m -s native.lua http://127.0.0.1:8080
}

function capture {
    # Execute wrk and capture the output
    output=$(benchmark)

    # Extract the average latency
    avg_latency=$(echo "$output" | grep "Latency" | awk '{print $2}')

    # Extract the standard deviation of latency
    stddev_latency=$(echo "$output" | grep "Latency" | awk '{print $3}')

    # Extract the throughput (requests per second)
    throughput=$(echo "$output" | grep "Requests/sec" | awk '{print $2}')

    echo $avg_latency > /tmp/$approach/latency-$workload.log
    echo -e "Latency Stdev: $stddev_latency, Throughput: $throughput" > $LOGS_HOME/$approach-$workload.txt
}

function warmup {
    # Sequential
    for i in $(seq 14)
    do
        curl -s -X POST 127.0.0.1:8080 -H 'Content-Type: application/json' -d $(cat /tmp/payload.post) &>/dev/null 
    done

    # Concurrent
    (
    for i in $(seq 14)
    do
        curl -s -X POST 127.0.0.1:8080 -H 'Content-Type: application/json' -d $(cat /tmp/payload.post) &>/dev/null &
    done
    wait
    )
}

function execute {
    # Faastion process pool requirement
    rm -rf /tmp/fifo
    mkdir -p /tmp/fifo
    
    # Start Graalvisor
    start_svm &> $LOGS_HOME/$approach-$workload-lambda.log &
    PID=$(echo -n "$!")

    # Log Resources (memory and CPU)
    log_resources $PID &

    # Register application
    $app

    # Comment for cold-start measures
    warmup
    
    # Run Benchmarking tool
    #capture
    benchmark
    
    # Kill Graalvisor and Webserver
    pkill -9 -f polyglot-proxy
}

function cleanup_resources {
    echo "Received signal, cleaning up resources..."
    pkill -9 -f polyglot-proxy
    exit
}

# Preparing global paths.
if [ -z "${ARGO_HOME}" ]; then
    echo "ARGO_HOME is not defined. Existing..."
    exit 1
fi
if [ "$#" -ne 1 ]; then
    echo "Syntax: <app>"
    echo "- app=<gv_java_native_matrix|gv_java_native_factors|...>"
    exit 1
else
    app=$1
fi

# Clean resources if killed with signal
trap 'cleanup_resources' SIGINT

rm -rf $LOGS_HOME
mkdir -p $LOGS_HOME

### SCRIPT STARTS HERE ###
nrequests=(1 2 4 8 12 16 20)

# JNI compilation
#compile_jni_benchmarks

export SANDBOX=isolate
for approach in faastion #faastlane 
do
    echo -e "${GREEN}###################################################"
    echo -e "#         Measuring metrics for $approach         #"
    echo -e "###################################################${NC}"
    
    rm -rf /tmp/$approach
    mkdir -p /tmp/$approach

    [ "$approach" = "faastlane" ] && export EAGER_MPK=1
    for workload in "${nrequests[@]}"
    do
        execute
    done
    [ "$approach" = "faastlane" ] && unset EAGER_MPK
done

# Normal compilation
# compile_benchmarks

# for approach in process isolate 
# do
#     echo -e "${GREEN}###################################################"
#     echo -e "#         Measuring metrics for $approach         #"
#     echo -e "###################################################${NC}"

#     rm -rf /tmp/$approach
#     mkdir -p /tmp/$approach

#     export SANDBOX=$approach
#     for workload in "${nrequests[@]}"
#     do
#         execute
#     done
# done

# Generate plots
#python3 latency.py

# Clean resources when finished
cleanup_resources