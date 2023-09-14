#!/bin/bash

# Setting up environment.
ip=127.0.0.1
start_svm &> $tmpdir/lambda.log &

# Let the lambda start.
wait_port $ip 8080

PID=$(cat $tmpdir/lambda.pid)

# Write lambda pid to file.
echo -n "$PID" > $tmpdir/lambda.pid

# Log memory.
log_rss $PID $tmpdir/lambda.rss &