#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

function generate_dataset {
    $AZURE_DATASET_HOME/trace-generator.sh -m 100 -d d01 -t $TRACES_HOME/result.csv
}

function extract_functions {
    python3 benchmark_assignment.py -f $NUM_FUNCTIONS -o $TRACES_HOME/trace.csv
}

function start_svm {
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    export lambda_port="8081"
    export LD_LIBRARY_PATH=$GRAALVISOR_HOME/build/libs:$LD_LIBRARY_PATH
    export LD_PRELOAD=$GRAALVISOR_HOME/build/libs/libtest.so

    # Start Graalvisor
    $GRAALVISOR_HOME/build/native-image/polyglot-proxy &
    wait
}

function compile_java_classes {
    javac -cp $CLASSPATH/lib/commons-cli-1.6.0/commons-cli-1.6.0.jar $CLASSPATH/*.java
}

function compile_benchmarks {
    dir_prefix="gv-native-hw-"

    # Iterate over directories
    for dir in "${BENCHMARKS}/${dir_prefix}"*; do
        if [ -d "$dir" ]; then            
            cd "$dir" || exit
            
            ./build_script.sh

            cd - || exit
        fi
    done
}

function execute {
    start_svm &> logs/lambda.log &

    java -cp $CLASSPATH ExecutorEntryPoint \
        -i      $TRACES_HOME/trace.csv  \
        -fc     $JAVA_BENCHMARKS/gv-native-hw-1/build/libnativehw1.so   \
        -fep    com.jni.HelloJNI \
        -nf     $NUM_FUNCTIONS
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
compile_java_classes
execute