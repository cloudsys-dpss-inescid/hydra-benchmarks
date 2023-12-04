APP_POST1=/tmp/payload1.post
APP_POST2=/tmp/payload2.post

function gv_java_native_hw {
    APP_LANG=java
    APP_NAME=gv-native-hw
    APP_SO=/home/cidra/git/graalserverless/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativehw.so
    APP_MAIN=com.jni.HelloJNI
    curl -s -X POST 127.0.0.1:8080/register?name=nativehw\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativehw","async":"false","cached":"true","arguments":""}' > $APP_POST1
}

function gv_java_native_hw_2 {
    APP_LANG=java
    APP_NAME=gv-native-hw-2
    APP_SO=/home/cidra/git/graalserverless/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativehw2.so
    APP_MAIN=com.jni.HelloJNI
    curl -s -X POST 127.0.0.1:8080/register?name=nativehw2\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativehw2","async":"false","cached":"true","arguments":""}' > $APP_POST2
}

gv_java_native_hw
gv_java_native_hw_2

curl -s -X POST 127.0.0.1:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST1) &
curl -s -X POST 127.0.0.1:8080 -H 'Content-Type: application/json' -d $(cat $APP_POST2) &

wait
