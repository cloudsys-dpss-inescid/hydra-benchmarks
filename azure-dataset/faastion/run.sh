#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

function build_azure {
    cd $AZURE_DATASET_HOME
    ./build.sh
    ./download_dataset.sh
    cd -
}

function generate_dataset {
    # Uncomment if azure-dataset is first time running
    # build_azure
    $AZURE_DATASET_HOME/trace-generator.sh -m 100 -d d01 -t $TRACES_HOME/gen-trace.csv
}

function extract_functions {
    python3 benchmark_assignment.py -f $NUM_FUNCTIONS -i $TRACES_HOME/gen-trace.csv -o $TRACES_HOME/trace.csv
}

function log_resources {
    PID=$1
    OFILE_RSS=/tmp/$approach/footprint.csv

    rm $OFILE_RSS &> /dev/null
        while kill -0 $PID &> /dev/null; do
                # The idea for memory is that we traverse the entire pid subprocess tree
                # and memory memory utilization. We sum all individual memory and return.
                s_mem=0
                timestamp=$(date -u +"%s")
                for p in $(pstree -p $PID | grep -o '([0-9]\+)' | grep -o '[0-9]\+')
                do
                    p_mem=$(ps -q $p -o rss=)
                    s_mem=$((s_mem + p_mem))
                done
                echo "$s_mem,$timestamp" >> $OFILE_RSS
                sleep .100
        done
}

function start_svm {
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    export lambda_port="8081"
    
    # Faastion process pool requirement
    mkdir -p /tmp/fifo
    
    export LD_LIBRARY_PATH=$GRAALVISOR_HOME/build/libs:$LD_LIBRARY_PATH
    export LD_PRELOAD=$GRAALVISOR_HOME/build/libs/libpreload.so
    # Start Graalvisor
    $GRAALVISOR_HOME/build/native-image/polyglot-proxy &
    wait
    unset LD_PRELOAD
}

function compile_java_classes {
    ./gradlew clean shadowJar
}

function compile_benchmarks {
    for benchmark in gv-file-hashing gv-genericapp gv-httprequest gv-native-factorization gv-native-hw-1 gv-native-matrixmul gv-sleep #gv-classify gv-video-processing
    do
        cd "$JAVA_BENCHMARKS/$benchmark"
        ./build_script.sh
        cd -
    done
}

function execute {
    # Start Graalvisor
    start_svm &> logs/lambda.log &
    PID=$(echo -n "$!")

    # Log Resources (memory and CPU)
    log_resources $PID &

    JAR=$(DIR)/build/libs/trace-executor-1.0-all.jar
    MAIN=ExecutorEntryPoint
    
    $JAVA_HOME/bin/java -cp $JAR $MAIN \
        -i      $TRACES_HOME/trace.csv  \
        -nf     $NUM_FUNCTIONS \
        -a      $approach \
        -d
    
    # Kill Graalvisor
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

GRAALVISOR_HOME=$ARGO_HOME/graalvisor
BENCHMARKS_HOME=$ARGO_HOME/benchmarks
AZURE_DATASET_HOME=$BENCHMARKS_HOME/azure-dataset
JAVA_BENCHMARKS=$BENCHMARKS_HOME/src/java

LOGS_HOME=$(DIR)/logs
TRACES_HOME=$(DIR)/traces

# Change if needed
NUM_FUNCTIONS=1

### SCRIPT STARTS HERE ###
mkdir -p $TRACES_HOME
mkdir -p $LOGS_HOME

# Clean resources if killed with signal
trap 'cleanup_resources' SIGINT

generate_dataset
extract_functions
compile_java_classes

for approach in faastion #faastlane isolates process
do
    mkdir -p /tmp/$approach
    compile_benchmarks
    execute
done
