
#copy line in my machine: 
#cp -r ~/work/argo/benchmarks/results/benchmark/java/* ~/work/argo/benchmarks/results/experiment/scheduler-overhead/results/java/CClient/
#export WMULTIPLIER=50280



export WMULTIPLIER=131072  #8192
export SERVER_IP=10.15.0.24 #vitamina04 10.15.0.24
export CLIENT_IP=10.15.0.25  #vitamina05 10.15.0.25
export CLIENT_USERNAME="claudiocorreia" #
export CLIENT_DIR="/home/claudiocorreia/remoteClient" #

#export WMULTIPLIER=2000


export verbose_benchmark=true

export WMULTIPLIER=16384



# Prompt the user for the SSH password
if [ -z "$SSH_PASSWORD" ]; then
    echo -n "SSH Password for $USERNAME@$CLIENT_IP: "
    read -s SSH_PASSWORD
    echo
    export SSH_PASSWORD
fi



./benchmark-graalvisor-remote.sh svm gv_java_httprequest 1 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 2 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 4 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 8 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 16 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 32 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 64 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 128 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 256 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 512 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 1024 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR

mv ~/work/argo/benchmarks/results/benchmark/java/* ~/work/argo/benchmarks/results/experiment/scheduler-overhead/results/java/CClientBenchmark/


export verbose_benchmark=false


./benchmark-graalvisor-remote.sh svm gv_java_httprequest 1 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 2 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 4 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 8 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 16 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 32 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 64 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 128 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 256 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 512 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR
./benchmark-graalvisor-remote.sh svm gv_java_httprequest 1024 $CLIENT_IP $CLIENT_USERNAME  $CLIENT_DIR

mv ~/work/argo/benchmarks/results/benchmark/java/* ~/work/argo/benchmarks/results/experiment/scheduler-overhead/results/java/CClientClean/
