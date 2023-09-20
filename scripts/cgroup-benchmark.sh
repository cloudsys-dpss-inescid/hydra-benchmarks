#!/bin/bash

function DIR {
   echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

function test_java_hw {
    # Writing post file to disk
    mkdir $tmpdir/hw &> /dev/null
    APP_POST=$tmpdir/hw/payload.post
    gv_java_hw
    echo '{"name":"hw","async":"false","cached":"true","arguments":"","cpuCgroupQuota":"10000"}' > $APP_POST
    for i in $(seq 1 $number_of_tests)
    do
        pretime
        curl -s -X POST $ip:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST)
        postime
    done
}

function test_java_fh {
    # Writing post file to disk
    mkdir $tmpdir/fh &> /dev/null
    APP_POST=$tmpdir/fh/payload.post
    gv_java_filehashing
    echo '{"name":"filehashing","async":"false","true":"true","arguments":"{\"url\":\"http://'$IP':'$PORT'/snap.png\"}","cpuCgroupQuota":"10000"}' > $APP_POST
    for i in $(seq 1 $number_of_tests)
    do
        pretime
        curl -s -X POST $ip:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST)
        postime
    done
}

source $(DIR)/shared.sh
source $(DIR)/benchmarks.sh

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
    exit 1
else
    number_of_tests=$1
fi

# Setting a sandbox if not already set.
if [ -z "$SANDBOX" ]
then
    export SANDBOX=isolate
fi

# Preparing working directory
sudo rm -r $tmpdir/ &> /dev/null
mkdir $tmpdir &> /dev/null

# Setting up environment.
ip=127.0.0.1
start_svm &> $tmpdir/lambda.log &

# Let the lambda start.
wait_port $ip 8080

PID=$(cat $tmpdir/lambda.pid)

# Write lambda pid to file.
# echo -n "$PID" > $tmpdir/lambda.pid ############### Do I need this?

# Log memory.
# log_rss $PID $tmpdir/lambda.rss & ############### Do I need this?

# Run test/benchmark.
test_java_hw &> $tmpdir/hello_world.log &
HW_PID=$!
test_java_fh &> $tmpdir/file_hashing.log &
FH_PID=$!

wait $HW_PID
wait $FH_PID

# Teardown the lambda.
stop_svm