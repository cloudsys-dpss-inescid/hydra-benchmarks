#!/bin/bash

# Getting the local default ip used to connect to the internet.
IP=$(ip route get 8.8.8.8 | grep -oP  'src \K\S+')
PORT=8000

function DIR {
   echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

function gv_java_hw {
    APP_LANG=java
    APP_NAME=gv-hello-world
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libhelloworld.so
    APP_MAIN=com.hello_world.HelloWorld
    curl -s -X POST $ip:8080/register?name=hw\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&cpuCgroupQuota=100000 -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"hw","async":"false","cached":"$1","arguments":""}' > $APP_POST
}

function test_java_hw {
    APP_POST=$tmpdir/payload.post
    gv_java_hw
    for i in $(seq 1 $number_of_tests)
    do
        pretime
        curl -s -X POST $ip:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST)
        postime
    done
}

function gv_java_filehashing {
    APP_LANG=java
    APP_NAME=gv-file-hashing
    APP_MAIN=com.filehashing.FileHashing
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libfilehashing.so
    curl -s -X POST $ip:8080/register?name=filehashing\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&cpuCgroupQuota=50000 -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"filehashing","async":"false","cached":"true","arguments":"{\"url\":\"http://'$IP':'$PORT'/blob\"}"}' > $APP_POST
}

function test_java_fh {
    # Writing post file to disk
    mkdir $tmpdir/fh &> /dev/null
    APP_POST=$tmpdir/fh/payload.post
    gv_java_filehashing
    for i in $(seq 1 $number_of_tests)
    do
        pretime
        curl -s -X POST $ip:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST)
        postime
    done
}

function run_test_and_plot {
    test_name=$1
    sandbox_cache=$2
    cgroup_cache=$3

    if $sandbox_cache ; then
        label="cacheSB_"
    else
        label="noCacheSB_"
    fi

    if $cgroup_cache ; then
        export use_cpu_cache=true
        label="$label""cacheCgroup"
    else
        export use_cpu_cache=false
        label="$label""noCacheCgroup"
    fi

    runtmpdir=$tmpdir/$test_name
    mkdir -p $runtmpdir &> /dev/null

    # Setting up environment.
    ip=127.0.0.1
    start_svm &> $runtmpdir/lambda.log &

    # Let the lambda start.
    wait_port $ip 8080

    PID=$(cat $tmpdir/lambda.pid)

    # Run test/benchmark.
    if [ "$test_name" = "hw" ]; then
        test_java_hw $sandbox_cache &> $runtmpdir/run.log &
    # elif [$test_name = "fh"]
    # then
    #     test_java_fh &> $runtmpdir/run.log &
    else
        echo "Unknown test name"
        exit 1
    fi

    RUN_PID=$!

    wait $RUN_PID

    # Teardown the lambda.
    stop_svm

    # Remove main cgroup
    start=$(date +%s%N)
    rmdir /sys/fs/cgroup/user.slice/user-1000.slice/isolate/cgroup-*
    rmdir /sys/fs/cgroup/user.slice/user-1000.slice/isolate
    end=$(date +%s%N)
    echo "Removing cgroup took $((($end - $start)/1000)) us"

    plotsDir=$runtmpdir/plots/$label
    sudo mkdir -p $plotsDir

    python3 main.py $runtmpdir/run.log "process time" $plotsDir "hwProcessTime" $label
    python3 main.py $runtmpdir/run.log "Time taken" $plotsDir "hwTimeTaken" $label
    python3 main.py $runtmpdir/lambda.log "New" $plotsDir "newCgroupTimes" $label
    python3 main.py $runtmpdir/lambda.log "Inserted" $plotsDir "insertCgroupTimes" $label
    python3 main.py $runtmpdir/lambda.log "Removed" $plotsDir "removeCgroupTimes" $label
}

source $(DIR)/shared.sh

if [ "$#" -ne 1 ]; then
    echo "Illegal number of parameters"
    exit 1
else
    number_of_tests=$1
fi

# Setting a sandbox if not already set.
if [ -z "$SANDBOX" ]; then
    export SANDBOX=isolate
fi

# Preparing working directory
rm -r $tmpdir &> /dev/null
mkdir -p $tmpdir &> /dev/null

run_test_and_plot "hw" true true
run_test_and_plot "hw" true false
run_test_and_plot "hw" false true
run_test_and_plot "hw" false false