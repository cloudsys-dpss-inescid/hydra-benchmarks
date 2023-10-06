#!/bin/bash

# Example usage of this script:
# bash benchmark-svm-load.sh /path/to/dataset/file
# The structure of the .csv file should be as follows:
# HashOwner HashFunction AverageAllocatedMb AverageDuration Timestamp

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/shared.sh


function start_gv {
    port=$1

    # Prepare working directory.
    cp $ARGO_HOME/graalvisor/build/native-image/polyglot-proxy $TEMP_DIR/app
    cd $TEMP_DIR

    # Launch a Graalvisor instance and log its PID.
    lambda_timestamp="$(date +%s%N | cut -b1-13)" lambda_port="$port" $TEMP_DIR/app &
    echo -n "$!" > "$TEMP_DIR/lambda.pid"
    wait
}

function process_dataset {
    csv_file=$1
    function_code=$2
    function_entry_point=$3
    gv_address=$4
    isolate_caching=$5

    AZURE_EXECUTOR_JAR=$(DIR)/../azure-dataset/build/libs/azure-dataset-1.0-all.jar
    AZURE_EXECUTOR_ENTRYPOINT=org.graalvm.argo.dataset.execution.SvmExecutorEntryPoint

    time $JAVA_HOME/bin/java -cp $AZURE_EXECUTOR_JAR $AZURE_EXECUTOR_ENTRYPOINT \
        --input $csv_file \
        --functionCode $function_code \
        --functionLanguage java \
        --functionEntryPoint $function_entry_point \
        --gvProxyAddress $gv_address \
        --gvCache $isolate_caching

    sleep 60
    echo "Finished benchmark execution."
}

DATASET_FILE=$1

# Default values for some variables.
if [ -z "${GV_PORT}" ]; then
    GV_PORT="8080"
fi
if [ -z "${ISOLATE_CACHING}" ]; then
    ISOLATE_CACHING="true"
fi
if [ -z "${FUNCTION_CODE}" ]; then
    FUNCTION_CODE=$ARGO_HOME/../benchmarks/src/java/gv-database-read/build/libdbread.so
fi
FUNCTION_ENTRY_POINT=com.dbread.DbRead

GV_IP="127.0.0.1"
GV_ADDRESS="$GV_IP:$GV_PORT"
TEMP_DIR="/tmp/test-proxy-$GV_PORT"
sudo rm -r $TEMP_DIR/ &> /dev/null
mkdir $TEMP_DIR &> /dev/null

# Deploy GV and wait for it to launch
start_gv $GV_PORT &> $TEMP_DIR/lambda.log &
wait_port $GV_IP $GV_PORT

PID=$(cat $TEMP_DIR/lambda.pid)
log_rss $PID $TEMP_DIR/lambda.rss &

process_dataset $DATASET_FILE $FUNCTION_CODE $FUNCTION_ENTRY_POINT $GV_ADDRESS $ISOLATE_CACHING

sudo kill "$PID"

echo "Finished executing experiment on port $GV_PORT."
