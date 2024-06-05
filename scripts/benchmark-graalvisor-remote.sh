#!/bin/bash

function DIR {
    echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

source $(DIR)/shared.sh

CLIENT_CODE_DIR="/http-loader"

function run_remote_client {



    # Assuming $1 to $6 are the parameters for the http_post executable
    #local SERVER_IP="$1"
    #local SERVER_PORT="$2"
    #local PAYLOAD_FILE="$3"
    local LOCAL_THREADS="$1"
    local WORKLOAD="$2"
    #local REMOTE_RESULTS_DIR="$6"
    local LOCAL_RESULTS_DIR="$3"

    #only now the payload is ready and available to be send to the remote client
    sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r "$TDIR/payload.post" "$USERNAME@$CLIENT_IP:$REMOTE_DIRECTORY_CODE" >> $TDIR/remote_client.log  2>&1

    
    #printf "\n\n a fazer pedido aqui\n"
    #printf "\n\n pedido: && ./http_post $SERVER_IP $SERVER_PORT $REMOTE_PAYLOAD_FILE $LOCAL_THREADS $WORKLOAD $REMOTE_RESULTS_DIR    e  $USERNAME@$CLIENT_IP" "ulimit -n 16384 && cd $SSH_PASSWORD "
    sshpass -p "$SSH_PASSWORD" ssh  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$USERNAME@$CLIENT_IP" "ulimit -n 1048576 && cd $REMOTE_DIRECTORY_CODE && ./http_post $SERVER_IP $SERVER_PORT $REMOTE_PAYLOAD_FILE $LOCAL_THREADS $WORKLOAD $REMOTE_RESULTS_DIR"  >> $TDIR/remote_client.log  2>&1
    #sshpass -p "$SSH_PASSWORD" ssh  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$USERNAME@$CLIENT_IP" " cd $REMOTE_DIRECTORY_CODE && ./http_post $SERVER_IP $SERVER_PORT $REMOTE_PAYLOAD_FILE $LOCAL_THREADS $WORKLOAD $REMOTE_RESULTS_DIR"  >> $TDIR/remote_client.log  2>&1
    #printf "\n\n a enviar os datapoints\n"
    sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r "$USERNAME@$CLIENT_IP:$REMOTE_RESULTS_DIR*" "$TDIR" >> $TDIR/remote_client.log  2>&1
    #printf "\n\n  datapoints enviados \n"



    
    # Build the project on the remote server
    #TDIR2="/home/ccorreia/tmp/test-proxy/" 

    # Execute the built executable with parameters on the remote server
    #sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$USERNAME@$CLIENT_IP" "cd $REMOTE_DIRECTORY_CODE && ./http_post $param1 $param2 $param3 $param4 $param5 $param6" &> $TDIR/remote_client.log

    # Copy the results from the remote server to the local machine
    #sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r "$USERNAME@$CLIENT_IP:$REMOTE_DIRECTORY_CODE/results/" "$LOCAL_DIR_PATH/results/" &> $TDIR/remote_client.log

    # <host> <porta> <arquivo_payload> <#threads> <workload> <results_directory>

    #run_remote_client "146.193.41.25" "8080" "payload.post" "2" "200" "$REMOTE_DIRECTORY_CODE/results"






}

# Check if BENCHMARK_FLAG is set to -1; if so, exit the script early
if [[ "$REMOTE_BENCHMARK_FLAG" == "-1" ]]; then
    #echo "Flag is set to -1, exiting script early."
    return 0  # Use 'return' instead of 'exit' when sourcing scripts
fi


# Check if the correct number of arguments was passed
if [ "$#" -ne 6 ]; then
    echo "Usage: $0 <svm|container|vm> <app> <# of tests or concurrency level> <client IP> <username> <client working directory>"
    echo "you can also deifne SERVER_IP and WMULTIPLIER as an export "
    echo "example: ./benchmark-graalvisor-remote.sh 146.193.41.248 intelnuc2 /home/intelnuc2/Downloads/graal_test/toDelete"
    exit 1
fi


if [ -z "$SERVER_IP" ]; then
    SERVER_IP=$(curl -s ifconfig.me)
    echo "Assuming Server address is: $SERVER_IP"
    export SERVER_IP
fi


# Assign input arguments to variables
BACKEND=$1
APP=$2
MODE="remote_Cclient_benchmark"
THREADS=$3
export CLIENT_IP=$4
export USERNAME=$5
REMOTE_DIRECTORY=$6
export SERVER_PORT=$GRAALVISOR_PORT
LOCAL_CLIENT_CODE_DIR=$BENCHMARKS_HOME$CLIENT_CODE_DIR
export REMOTE_DIRECTORY_CODE=$REMOTE_DIRECTORY$CLIENT_CODE_DIR
export REMOTE_PAYLOAD_FILE=$REMOTE_DIRECTORY_CODE/payload.post # This has also been defined in benchmark-graalvisor.sh
export REMOTE_RESULTS_DIR=$REMOTE_DIRECTORY_CODE/results/


# Prompt the user for the SSH password
if [ -z "$SSH_PASSWORD" ]; then
    echo -n "SSH Password for $USERNAME@$CLIENT_IP: "
    read -s SSH_PASSWORD
    echo
    export SSH_PASSWORD
fi



# Use sshpass and SSH to clear the remote directory
sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$USERNAME@$CLIENT_IP" "rm -r $REMOTE_DIRECTORY/*" >> $TDIR/remote_client.log  2>&1

# Use sshpass and scp with -r option to recursively copy the directory to the remote directory
sshpass -p "$SSH_PASSWORD" scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -r "$LOCAL_CLIENT_CODE_DIR" "$USERNAME@$CLIENT_IP:$REMOTE_DIRECTORY" >> $TDIR/remote_client.log  2>&1

sshpass -p "$SSH_PASSWORD" ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$USERNAME@$CLIENT_IP" "cd $REMOTE_DIRECTORY_CODE && make clean && make" >> $TDIR/remote_client.log  2>&1


./benchmark-graalvisor.sh $BACKEND $APP $MODE $THREADS