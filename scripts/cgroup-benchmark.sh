#!/bin/bash

# Getting the local default ip used to connect to the internet.
IP=$(ip route get 8.8.8.8 | grep -oP  'src \K\S+')
PORT=8000

function DIR {
   echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

function gv_java_filehashing {
    APP_LANG=java
    APP_NAME=gv-file-hashing
    APP_MAIN=com.filehashing.FileHashing
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libfilehashing.so
    curl -s -X POST $ip:8080/register?name=filehashing\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&cpuCgroupQuota=40000 -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"filehashing","async":"false","cached":"false","arguments":"{\"url\":\"http://'$IP':'$PORT'/blob\"}"}' > $APP_POST
}

function gv_java_hw {
    APP_LANG=java
    APP_NAME=gv-hello-world
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libhelloworld.so
    APP_MAIN=com.hello_world.HelloWorld
    curl -s -X POST $ip:8080/register?name=hw\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&cpuCgroupQuota=100000 -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"hw","async":"false","cached":"false","arguments":""}' > $APP_POST
}

function gv_java_videoprocessing {
    APP_LANG=java
    APP_NAME=gv-video-processing
    APP_MAIN=com.videoprocessing.VideoProcessing
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libvideoprocessing.so
    curl -s -X POST $ip:8080/register?name=videoprocessing\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&cpuCgroupQuota=50000 -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"videoprocessing","async":"false","arguments":"{\"video\":\"http://'$IP':'$PORT'/video.mp4\",\"ffmpeg\":\"http://'$IP':'$PORT'/ffmpeg\"}"}' > $APP_POST
}

function gv_java_classify {
    APP_LANG=java
    APP_NAME=gv-classify
    APP_MAIN=com.classify.Classify
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libclassify.so
    curl -s -X POST $ip:8080/register?name=classify\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&cpuCgroupQuota=100000 -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"classify","async":"false","arguments":"{\"model_url\":\"http://'$IP':'$PORT'/tensorflow_inception_graph.pb\",\"labels_url\":\"http://'$IP':'$PORT'/imagenet_comp_graph_label_strings.txt\",\"image_url\":\"http://'$IP':'$PORT'/eagle.jpg\"}"}' > $APP_POST
}

function gv_fibonnaci {
    APP_LANG=java
    APP_NAME=gv-fibonnaci
    APP_MAIN=com.fibonnaci.Fibonnaci
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libfibonnaci.so
    curl -s -X POST $ip:8080/register?name=fibonnaci\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&cpuCgroupQuota=100000 -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"fibonnaci","async":"false","arguments":"{\"term\":\"50\"}"}' > $APP_POST
}

function run_test {
    APP_POST=$runtmpdir/payload.post
    if [ "$test_name" = "hw" ]; then
        gv_java_hw
    elif [ "$test_name" = "fileHashing" ]; then
        gv_java_filehashing
    elif [ "$test_name" = "videoProcess" ]; then
        gv_java_videoprocessing
    elif [ "$test_name" = "imageClassify" ]; then
        gv_java_classify
    elif [ "$test_name" = "fibonnaci" ]; then
        gv_fibonnaci
    else
        echo "Unknown test name"
        exit 1
    fi

    for i in $(seq 1 $number_of_tests)
    do
        pretime
        curl -s -X POST $ip:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST)
        postime
        if (($i % ($number_of_tests/10) == 0)); then
           echo -en "$test_name ($i/$number_of_tests)\r" >&3
        fi
    done
    echo -en "\n" >&3
}

function run_test_and_plot {
    test_name=$1
    cgroup_cache=$2


    if $cgroup_cache ; then
        label="cacheCgroup"
    else
        label="noCacheCgroup"
    fi

    export use_cgroup_cache=$cgroup_cache

    echo "Running test $test_name with $label"

    runtmpdir=$tmpdir/$test_name/$label
    mkdir -p $runtmpdir &> /dev/null

    # Setting up environment.
    ip=127.0.0.1
    start_svm &> $runtmpdir/lambda.log &

    # Let the lambda start.
    wait_port $ip 8080

    PID=$(cat $tmpdir/lambda.pid)

    exec 3>&1

    # Run test/benchmark.
    run_test &> $runtmpdir/run.log &
    RUN_PID=$!
    wait $RUN_PID

    exec >&3 3>&-
    # Teardown the lambda.
    stop_svm
    sleep 1

    # Remove main cgroup
    start=$(date +%s%N)
    rmdir /sys/fs/cgroup/user.slice/user-1000.slice/gv-cgroups/cgroup-*
    rmdir /sys/fs/cgroup/user.slice/user-1000.slice/gv-cgroups
    end=$(date +%s%N)
    echo "Deleted cgroup (main and children) took $((($end - $start)/1000)) us" >> $runtmpdir/lambda.log

    plotsDir=$runtmpdir/plots
    sudo mkdir -p $plotsDir

#     python3 main.py $runtmpdir/run.log "process time" $plotsDir "ProcessTime" $label
#     python3 main.py $runtmpdir/run.log "Time taken" $plotsDir "TimeTaken" $label
#     python3 main.py $runtmpdir/lambda.log "Created cgroup-" $plotsDir "CreateCgroupTimes" $label
#     python3 main.py $runtmpdir/lambda.log "(deleted" $plotsDir "DeleteThreadCgroupTimes" $label
#     python3 main.py $runtmpdir/lambda.log "(added" $plotsDir "AddThreadCgroupTimes" $label
#     python3 main.py $runtmpdir/lambda.log "Deleted cgroup" $plotsDir "DeleteCgroupTimes" $label
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

#run_test_and_plot "hw" true
#run_test_and_plot "hw" false
#run_test_and_plot "fileHashing" true
#run_test_and_plot "fileHashing" false
#run_test_and_plot "videoProcess" true
#run_test_and_plot "videoProcess" false
#run_test_and_plot "imageClassify" true
#run_test_and_plot "imageClassify" false
run_test_and_plot "fibonnaci" true
#run_test_and_plot "fibonnaci" false

echo "Done"



