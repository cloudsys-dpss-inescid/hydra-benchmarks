export lambda_timestamp="$(date +%s%N | cut -b1-13)"
export lambda_port="8081"

export LD_LIBRARY_PATH=$ARGO_HOME/graalvisor/build/libs:$LD_LIBRARY_PATH
for i in $(seq $1)
do
    export LD_LIBRARY_PATH=$ARGO_HOME/benchmarks/src/java/gv-native-hw-$i/build/libs:$LD_LIBRARY_PATH
done
#export LD_LIBRARY_PATH=$ARGO_HOME/benchmarks/src/java/gv-native-aes/build/libs:$LD_LIBRARY_PATH
export LD_PRELOAD=$ARGO_HOME/graalvisor/build/libs/libtest.so
gdb /home/cidra/git/graalserverless/graalvisor/build/native-image/polyglot-proxy
