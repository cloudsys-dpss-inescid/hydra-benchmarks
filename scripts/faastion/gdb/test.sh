function gv_java_native_hw_n {
    APP_LANG=java
    APP_NAME=gv-native-hw-$1
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativehw$1.so
    APP_MAIN=com.jni.HelloJNI
    # Register the native application in GraalVM
    curl -s -X POST 127.0.0.1:8081/register?name=nativehw$1\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativehw'$1'","async":"false","cached":"true","arguments":""}' > /tmp/payload$1.post
}

for i in $(seq $1)
do
    gv_java_native_hw_n $i
done


for i in $(seq $1)
do
    # Send requests to Graalvisor for each application
    curl -s -X POST 127.0.0.1:8081 -H 'Content-Type: application/json' -d $(cat /tmp/payload$i.post) &
done

wait
