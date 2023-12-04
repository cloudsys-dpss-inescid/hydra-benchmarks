export lambda_timestamp="$(date +%s%N | cut -b1-13)"
export lambda_port="8080"

export LD_LIBRARY_PATH=$ARGO_HOME/graalvisor/build/libs:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$ARGO_HOME/benchmarks/src/java/gv-native-hw/build/libs:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$ARGO_HOME/benchmarks/src/java/gv-native-hw-2/build/libs:$LD_LIBRARY_PATH

export LD_PRELOAD=$ARGO_HOME/graalvisor/build/libs/libtest.so
gdb /home/cidra/git/graalserverless/graalvisor/build/native-image/polyglot-proxy
