#!/bin/bash

# Function to register Java applications in GraalVM
function gv_java_native_hw_n {
    APP_LANG=java
    APP_NAME=gv-native-hw-$1
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativehw$1.so
    APP_MAIN=com.jni.HelloJNI
    # Register the native application in GraalVM
    curl -s -X POST 127.0.0.1:8081/register?name=nativehw$1\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativehw'$1'","async":"false","cached":"true","arguments":""}' > /tmp/payload$1.post
}

# Function to start the Graalvisor
function start_svm {
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    export lambda_port="8081"
    export LD_LIBRARY_PATH=$ARGO_HOME/graalvisor/build/libs:$LD_LIBRARY_PATH

    # Add native library paths for each application
    for i in $(seq $ndomains)
    do
        export LD_LIBRARY_PATH=$ARGO_HOME/benchmarks/src/java/gv-native-hw-$i/build/libs:$LD_LIBRARY_PATH
    done
    export LD_PRELOAD=$ARGO_HOME/graalvisor/build/libs/libtest.so

    # Start Graalvisor
    $ARGO_HOME/graalvisor/build/native-image/polyglot-proxy &
    wait
}

function warmup {
    for j in $(seq $ndomains)
    do
        curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d $(cat /tmp/payload$j.post) >/dev/null
    done

    if [ "$ndomains" -eq 2 ]
    then
        (
            for j in $(seq 2)
            do
                curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d $(cat /tmp/payload$j.post) &>/dev/null &
            done
            wait
        )
    fi

    if [ "$ndomains" -ge 3 ]
    then
        (
            for j in $(seq 3)
            do
                curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d $(cat /tmp/payload$j.post) &>/dev/null &
            done
            wait
        )
    fi

}

# Function to run the workload
function run {
    nrun=$1

    # Start Graalvisor and capture execution time information
    start_svm 2>&1 | tee logs/lambda-$nrun.log | grep -E "Execution time" > logs/filtered_lambda-$nrun.log &

    # Register Java native applications in Graalvisor
    for i in $(seq $ndomains)
    do
        gv_java_native_hw_n $i
    done
    
    warmup

    # Execute the workload for each domain
    for i in $(seq $workload)
    do
        (            
            for j in $(seq $ndomains)
            do
                # Send requests to Graalvisor for each application
                curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d $(cat /tmp/payload$j.post) &>> logs/ab$j-$nrun.log &
            done
            
            # Wait for all background processes to finish
            wait
        )

        # Add a newline to each domain log file
        for j in $(seq $ndomains)
        do
            echo "" >> logs/ab$j-$nrun.log
        done
    done

    # Kill Graalvisor
    pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
    kill $pid
}

# Start

if [ "$#" -ne 2 ]; then
    echo "Syntax: <# of tests> <# of domains>"
else
    workload=$1
    ndomains=$2
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
python3 domains.py -d $ndomains
