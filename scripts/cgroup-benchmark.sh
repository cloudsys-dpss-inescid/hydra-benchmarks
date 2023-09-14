#!/bin/bash

function DIR {
   echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

function test {
    for i in $(seq 1 100)
    do
        pretime
        curl -s -X POST $ip:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST) &
        postime
    done
}


source $(DIR)/shared.sh
source $(DIR)/benchmarks.sh

# Setting a sandbox if not already set.
if [ -z "$SANDBOX" ]
then
    export SANDBOX=isolate
fi

# Writing post file to disk
APP_POST=$tmpdir/payload.post

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

# Load function into runtime.
gv_java_hw

# Run test/benchmark.
test | tee -a $tmpdir/app.log

# Teardown the lambda.
stop_svm