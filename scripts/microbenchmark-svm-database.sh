#!/bin/bash

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

function run_microbenchmark {
    GV_PORT=$1
    FUNCTION_CODE=$2
    ITERATIONS=$3

    ISOLATE_CACHING="true"
    FUNCTION_ENTRY_POINT="com.dbread.DbRead"

    GV_IP="127.0.0.1"
    GV_ADDRESS="$GV_IP:$GV_PORT"
    TEMP_DIR="/tmp/test-proxy-$GV_PORT"
    sudo rm -r $TEMP_DIR/ &> /dev/null
    mkdir $TEMP_DIR &> /dev/null

    # Deploy GV and wait for it to launch
    start_gv $GV_PORT &> $TEMP_DIR/lambda.log &
    wait_port $GV_IP $GV_PORT
    PID=$(cat $TEMP_DIR/lambda.pid)

    curl -X POST $GV_ADDRESS/register?name=dbread\&entryPoint=$FUNCTION_ENTRY_POINT\&language=java\&sandbox=isolate -H 'Content-Type: application/json' --data-binary @"$FUNCTION_CODE"
    result=$(curl -X POST $GV_ADDRESS -H 'Content-Type: application/json' -d '{"name":"dbread","async":"false","cached":"'$ISOLATE_CACHING'","arguments":"{\"iterations\":\"'$ITERATIONS'\"}"}')

    # Get result field and remove all slashes.
    result=$(echo $result | jq '.result' | sed 's/\\//g')
    # Remove first and last quote and retrieve the time field.
    echo $result | tail -c +2 | head -c -2 | jq '.' &> $TEMP_DIR/result.json

    sudo kill "$PID"
    echo "Finished executing experiment on port $GV_PORT."
}


DBREAD_FUNCTION_CODE=$ARGO_HOME/../benchmarks/src/java/gv-database-read/build/libdbread.so
DBREAD_NO_PERS_FUNCTION_CODE=$ARGO_HOME/../benchmarks/src/java/gv-database-read-no-cache/build/libdbread.so

run_microbenchmark 8081 $DBREAD_FUNCTION_CODE 10
run_microbenchmark 8082 $DBREAD_NO_PERS_FUNCTION_CODE 10
