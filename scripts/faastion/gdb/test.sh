function gv_java_native_hw_n {
    APP_LANG=java
    APP_NAME=gv-native-hw-$1
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativehw$1.so
    APP_MAIN=com.jni.HelloJNI
    # Register the native application in GraalVM
    curl -s -X POST 127.0.0.1:8081/register?name=nativehw$1\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativehw'$1'","async":"false","cached":"true","arguments":""}' > /tmp/payload$1.post
}

function gv_java_native_matrix {
    APP_LANG=java
    APP_NAME=gv-native-matrixmul
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libmatrixmul.so
    APP_MAIN=com.jni.MatrixMultiplication
    # Register the native application in GraalVM
    curl -s -X POST 127.0.0.1:8081/register?name=matrixmul\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"matrixmul","async":"false","cached":"true","arguments":""}' > /tmp/payload-rodrigo.post
}

function gv_java_native_factors {
    APP_LANG=java
    APP_NAME=gv-native-factorization
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libfactors.so
    APP_MAIN=com.jni.Factorization
    curl -s -X POST 127.0.0.1:8081/register?name=factors\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"factors","async":"false","cached":"true","arguments":""}' > /tmp/payload-rodrigo.post
}

function gv_java_native_aes {
    APP_LANG=java
    APP_NAME=gv-native-aes
    APP_SO=$ARGO_HOME/benchmarks/src/$APP_LANG/$APP_NAME/build/libnativeaes.so
    APP_MAIN=com.jni.AESEncryption
    # Register the native application in GraalVM
    curl -s -X POST 127.0.0.1:8081/register?name=nativeaes\&entryPoint=$APP_MAIN\&language=$APP_LANG -H 'Content-Type: application/json' --data-binary @$APP_SO
    echo '{"name":"nativeaes","async":"false","cached":"true","arguments":""}' > /tmp/payload-rodrigo.post
}

#for i in $(seq $1)
#do
#    gv_java_native_hw_n $i
#done

#gv_java_native_aes
#gv_java_native_matrix
gv_java_native_factors

wrk -t$1 -c$1 -d1s -s native.lua http://127.0.0.1:8081
