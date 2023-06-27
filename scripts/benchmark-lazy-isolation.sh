#!/bin/bash

ip=127.0.0.1
optargs=0
tmpdir=/tmp/test-proxy
sudo rm -r $tmpdir/ &> /dev/null
mkdir $tmpdir &> /dev/null
APP_POST=$tmpdir/payload.post
LAZY_HOME=

function usage {
    echo "Syntax: [-X proxy] [-n requests] [-C sec-profile-pathname] app"
}

function exit_abnormal {
    usage
    exit 1
}

while getopts ":X:n:C:" opt; do
	case $opt in
		X)
		  proxy=${OPTARG}
		  ;;
		n)
		  requests=${OPTARG}
		  ;;
		C)
		  sec_profile=${OPTARG}
		  ;;
        :)
          echo "Error: -$OPTARG requires an argument" >&2
          exit_abnormal
          ;;
		\?)
		  echo "Error: invalid option -$OPTARG" >&2
          exit_abnormal
	esac
    optargs=$((optargs+2))
done

if [ "$#" -lt 1 ] || [ "$#" -ne $((optargs+1)) ]; then
    echo "Error: app not provided" >&2
    exit_abnormal
fi

app=${@: -1}

if [ ! -z $proxy ]; then
    proxy_string="proxy=$proxy; "
fi
if [ -z $requests ]; then
    requests=100
fi
requests_string="requests=$requests; "
if [ ! -z $sec_profile ]; then
    sec_profile_string="sec_profile=$sec_profile; "
fi

echo "Running ${proxy_string}${requests_string}${sec_profile_string}app=$app"

function pretime {
    ts=$(date +%s%N)
}

function postime {
    tt=$((($(date +%s%N) - $ts)/1000))
    times+=($tt)
}

function benchmark {
    proxy=standalone
    if [ -z $sec_profile ]; then
        APP_LOADER="java -jar "
        sec_profile=allow-syscalls
    else
        APP_LOADER="$LAZY_HOME/build/bin/sys_filter_scmp --profile=$sec_profile java -jar "
        sec_profile=filter-syscalls
    fi

    times=()
    for i in $(seq 1 $requests)
	do
		pretime
		$APP_LOADER $APP &> "$tmpdir/app.log"
		postime
	done
    printf "%s\n" "${times[@]}" > "$tmpdir/benchmark.log"
}

function wait_port {
    sleep 1
    echo "Waiting for $ip:8080"
    while ! nc -z $ip 8080; do sleep 1; done
}

function start_proxy {
    # rm -rf apps
    export lambda_port=8080
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    $ARGO_HOME/graalvisor/build/native-image/polyglot-proxy &> "$tmpdir/proxy.log" &
    PID=$!
    wait_port
}

function register_app {
    curl -s -X POST $ip:8080/register?name=$NAME\&entryPoint=$APP_MAIN\&language=$APP_LANG\&sandbox=$SANDBOX\&lazy=$LAZY -H 'Content-Type: application/json' --data-binary @$APP_SO
}

function proxy_benchmark {
    if [ -z $sec_profile ]; then
        LAZY="false"
        sec_profile=allow-syscalls
    else
        LAZY="true"
        sec_profile=filter-syscalls
    fi

    register_app

    ab -p $APP_POST -T application/json -n $requests http://$ip:8080/ &> $tmpdir/ab-init.log
    ab -p $APP_POST -T application/json -n $requests http://$ip:8080/ &> $tmpdir/ab.log
}

function stop_proxy {
    sudo kill $PID
}

function java_hw {
    APP_LANG=java
    APP_NAME=gv-hello-world
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libhelloworld.so
    APP_MAIN=com.hello_world.HelloWorld
    APP=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libs/hello-world-1.0-all.jar
    SANDBOX=process
    NAME=hw
    echo '{"name":"'$NAME'","async":"false","cached":"true","arguments":""}' > "$APP_POST"
}

function java_filehashing {
    APP_LANG=java
    APP_NAME=gv-file-hashing
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libfilehashing.so
    APP_MAIN=com.filehashing.FileHashing
    APP=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libs/filehashing-1.0-all.jar
    SANDBOX=process
    NAME=filehashing
    echo '{"name":"'$NAME'","async":"false","cached":"true","arguments":"{\"url\":\"http://localhost:8000/snap.png\"}"}' > "$APP_POST"
}

function java_videoprocessing {
    APP_LANG=java
    APP_NAME=gv-video-processing
    APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libvideoprocessing.so
    APP_MAIN=com.videoprocessing.VideoProcessing
    APP=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libs/videoprocessing-1.0-all.jar
    SANDBOX=process
    NAME=videoprocessing
    echo '{"name":"'$NAME'","async":"false","cached":"true","arguments":"{\"ffmpeg\":\"http://localhost:8000/ffmpeg\",\"video\":\"http://localhost:8000/file_example_MP4_480_1_5MG.mp4\"}"}' > "$APP_POST"
}

function java_genericapp {
	APP_LANG=java
	APP_NAME=gv-genericapp
	APP_SO=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libgenericapp.so
	APP_MAIN=com.genericapp.GenericApp
	APP=$BENCHMARKS_HOME/src/$APP_LANG/$APP_NAME/build/libs/genericapp-1.0-all.jar
	SANDBOX=isolate
	NAME=genericapp
	echo '{"name":"'$NAME'","async":"false","cached":"true","arguments":"{\"memory\":\"100\",\"duration\":\"1000\"}"}' > "$APP_POST"
}

$app

if [ -z $proxy ]; then
    benchmark
    logfile=app.log
else
    start_proxy
    proxy_benchmark
    stop_proxy
    logfile=proxy.log
fi

results_dir=$BENCHMARKS_HOME/results/$APP_LANG/$APP_NAME-$proxy-$sec_profile-$requests
mkdir -p $results_dir &> /dev/null
cp -r $tmpdir/*.log $results_dir &> /dev/null
echo "Check logs: $results_dir/$logfile"
