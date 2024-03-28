export lambda_timestamp="$(date +%s%N | cut -b1-13)"
export lambda_port="8081"

export LD_LIBRARY_PATH=$ARGO_HOME/graalvisor/build/libs:$LD_LIBRARY_PATH
export LD_PRELOAD=$ARGO_HOME/graalvisor/build/libs/libpreload.so
gdb $ARGO_HOME/graalvisor/build/native-image/polyglot-proxy
