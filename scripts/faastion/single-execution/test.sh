APP_POST=/tmp/payload.post

function gv_java_native_aes {
    APP_LANG=java
    APP_NAME=gv-native-aes
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativeaes.so
    APP_MAIN=com.jni.AESEncryption
    curl -s -X POST 127.0.0.1:8081/register?name=nativeaes\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativeaes","async":"false","cached":"true","arguments":""}' > $APP_POST
}

function gv_java_native_hw_1 {
    APP_LANG=java
    APP_NAME=gv-native-hw-1
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativehw1.so
    APP_MAIN=com.jni.HelloJNI
    curl -s -X POST 127.0.0.1:8081/register?name=nativehw1\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativehw1","async":"false","cached":"true","arguments":""}' > $APP_POST
}

function start_svm {
    export lambda_timestamp="$(date +%s%N | cut -b1-13)"
    export lambda_port="8081"
    export LD_LIBRARY_PATH=$ARGO_HOME/graalvisor/build/libs:$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=$ARGO_HOME/benchmarks/src/java/gv-native-hw-1/build/libs:$LD_LIBRARY_PATH
    export LD_PRELOAD=$ARGO_HOME/graalvisor/build/libs/libtest.so
    $ARGO_HOME/graalvisor/build/native-image/polyglot-proxy &
    wait
}

function cleanup {
    files_to_remove=("/tmp/sandbox.log" "/tmp/graalvisor.log")

    for file in "${files_to_remove[@]}"; do
        if [ -e "$file" ]; then
            rm -f "$file"
        fi
    done
}

# Start
if [ "$#" -ne 1 ]; then
    echo "Syntax: <# of tests>"
else
    workload=$1
fi

mkdir -p results

start_svm | grep -E "sandbox time " | awk '{print $4}' > results/sandbox.log &

gv_java_native_hw_1

for i in $(seq $workload)
do
    curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d "$(cat $APP_POST)" | jq -r '.["process time (us)"] // empty' >> results/graalvisor.log
done

# Kill graalvisor
pid=$(pgrep -f "$ARGO_HOME/graalvisor/build/native-image/polyglot-proxy")
kill $pid
