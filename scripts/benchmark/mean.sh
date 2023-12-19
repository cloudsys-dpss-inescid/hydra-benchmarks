APP_POST1=/tmp/payload1.post

function gv_java_native_hw {
    APP_LANG=java
    APP_NAME=gv-native-hw
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativehw.so
    APP_MAIN=com.jni.HelloJNI
    curl -s -X POST 127.0.0.1:8080/register?name=nativehw\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativehw","async":"false","cached":"true","arguments":""}' > $APP_POST1
}

function start_svm {
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    export lambda_port="8080"
    export LD_LIBRARY_PATH=$ARGO_HOME/graalvisor/build/libs:$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=$ARGO_HOME/benchmarks/src/java/gv-native-hw/build/libs:$LD_LIBRARY_PATH
    export LD_PRELOAD=$ARGO_HOME/graalvisor/build/libs/libtest.so
    $ARGO_HOME/graalvisor/build/native-image/polyglot-proxy &
    wait
}

function benchmark {
    nrun="$1"

    start_svm 2>&1 | grep -E "Execution time" >> results/lambda-$nrun.log &

    gv_java_native_hw

    for i in $(seq $workload)
    do
        ab -p $APP_POST1 -T application/json -c 1 -n 1 127.0.0.1:8080/ | grep -E "Time per request:"&>> results/ab-$i.log
    done

    # Kill graalvisor
    pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
    kill $pid
}

function mean {
    for i in $(seq $1)
    do 
        benchmark $i
    done
}

# Start

if [ "$#" -ne 2 ]; then
    echo "Syntax: <# of tests> <aggregate|singular>"
else
    workload=$1
    execution=$2
fi

if [ -d "results" ]; then
    rm -rf "results"
fi
mkdir -p results

if [ "$execution" == "aggregate" ]; then
    ab -p $APP_POST1 -T application/json -c 1 -n $workload 127.0.0.1:8080/ | grep -E "Requests per second:|Time per request:"&> /tmp/ab.log
elif [ "$execution" == "singular" ]; then
    mean 10
fi

