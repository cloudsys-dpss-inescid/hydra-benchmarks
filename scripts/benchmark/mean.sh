APP_POST1=/tmp/payload1.post

if [ "$#" -ne 2 ]; then
    echo "Syntax: <# of tests> <aggregate|singular>"
else
    workload=$1
    execution=$2
fi

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

# Start graalvisor
start_svm &> /tmp/lambda.log &

# Register function
gv_java_native_hw

if [ "$execution" == "aggregate" ]; then
    ab -p $APP_POST1 -T application/json -c 1 -n $workload 127.0.0.1:8080/ | grep -E "Requests per second:|Time per request:"&> /tmp/ab.log
elif [ "$execution" == "singular" ]; then
    &> /tmp/ab.log &
    for ((i = 1; i <= $workload;i++))
    do
        ab -p $APP_POST1 -T application/json -c 1 -n 1 127.0.0.1:8080/ | grep -E "Requests per second:|Time per request:"&>> /tmp/ab.log
    done
fi

# Kill graalvisor
pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
kill $pid