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

function start_svm {
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    export lambda_port="8081"
    
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
    prefix="gv-native-hw-"

    # Iterate over directories
    for dir in "${BENCHMARKS}/${prefix}"*; do
        if [ -d "$dir" ]; then            
            cd "$dir"
            ./build_script.sh
            cd -
        fi
    done
}

function execute {
    start_svm &> logs/lambda.log &
    JAR=$(DIR)/build/libs/trace-executor-1.0-all.jar
    MAIN=ExecutorEntryPoint
    
    $JAVA_HOME/bin/java -cp $JAR $MAIN \
        -i      $TRACES_HOME/trace.csv  \
        -nf     $NUM_FUNCTIONS \
        -d
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
CLASSPATH=$(DIR)/java
TRACES_HOME=$(DIR)/traces

# Change if needed
NUM_FUNCTIONS=1

### SCRIPT STARTS HERE ###
mkdir -p $TRACES_HOME
mkdir -p $LOGS_HOME

generate_dataset
extract_functions
#compile_benchmarks
compile_java_classes
execute
