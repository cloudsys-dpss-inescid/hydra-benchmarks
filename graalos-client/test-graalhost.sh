#!/bin/bash

CONTAINER_NAME="graalos-container"
#export GRAALOS_SDK_DIR="/home/claudiocorreia/graalos_work/graalos"
CURRENT_DIR=$(pwd)

if [ -z "$GRAALOS_SDK_DIR" ]
then
    echo "Please set GRAALOS_SDK_DIR first. It should point to directory conainting an unziped version of the Graal IS SDK."
    exit 1
fi

tmpdir=${CURRENT_DIR}/logs/graalos-last
declare -i curl_counter=0

# Terminate graalhost:
function terminate_graalhost() {
    curl_counter+=1
    curl_tmpdir=${tmpdir}/curl-${curl_counter}
    mkdir -p ${curl_tmpdir}
    touch ${curl_tmpdir}/curl.header ${curl_tmpdir}/curl.stderr ${curl_tmpdir}/curl.stdout
    sed -e '/^[[:space:]]*$/d' >${curl_tmpdir}/curl.cmd <<EOF
curl --silent
     --show-error
     --write-out "%{http_code}"
     --output ${curl_tmpdir}/curl.stdout 
     --stderr ${curl_tmpdir}/curl.stderr
     --dump-header ${curl_tmpdir}/curl.header
     --max-time 3
     --unix-socket ${tmpdir}/graalhost.socket
     http://localhost/exit
EOF
    curl_cmd=$(<${curl_tmpdir}/curl.cmd)
    http_code=$(eval ${curl_cmd})
    curl_status=$?
    # expect to see something like the following : 
    # {"msg":"hub_1 exit command processed"}
    # HTTP/1.1 200 OK
    # Content-Type: application/json
    # Date: Tue, 28 Nov 2023 18:13:48 GMT # uWebSockets: 20
    # Content-Length: 39
    #
    if [[ ${verbose} == "yes" ]] ; then
        echo "${curl_cmd}" >&2
        cat ${curl_tmpdir}/curl.header >&2
        cat ${curl_tmpdir}/curl.stdout >&2
        cat ${curl_tmpdir}/curl.stderr >&2
    fi
    if [[ ${curl_status} != 0 || ! ${http_code} =~ ^2[0-9][0-9]$ ]] ; then
        echo "[ERROR] unable to terminate graalhost cleanly" >&2
        kill -9 ${graalhost_pid}
        exit 1
    fi
    
    wait ${graalhost_pid}
}

function load_aplication() {

    # The graalos management interface expects you to define an end point 
    # ID, which is unique to this instance of the hub:
    epid=2001

    # The isolate to run, example: ISOLATE=/scripts/apps/hello-world/helloworld
    ISOLATE=$1

    # Tell the hub to load a GraalAPP into memory and start a single 
    # isolate instance:
    curl_counter+=1
    curl_tmpdir=${tmpdir}/curl-${curl_counter}
    mkdir -p ${curl_tmpdir}
    touch ${curl_tmpdir}/curl.header ${curl_tmpdir}/curl.stderr ${curl_tmpdir}/curl.stdout
    sed -e '/^[[:space:]]*$/d' >${curl_tmpdir}/curl.cmd <<EOF
curl --silent
    --show-error
    --write-out "%{http_code}"
    --output ${curl_tmpdir}/curl.stdout
    --stderr ${curl_tmpdir}/curl.stderr
    --dump-header ${curl_tmpdir}/curl.header
    --max-time 3
    --unix-socket ${tmpdir}/graalhost.socket
    --data @${curl_tmpdir}/http_request_body.json
    http://localhost/command
EOF

    echo "Performing first curl, loading aplication"
    curl_cmd=$(<${curl_tmpdir}/curl.cmd)
    cat - >${curl_tmpdir}/http_request_body.json <<EOF 
{
    "act": "add_ep",
    "app": "${ISOLATE}",
    "ep": ${epid},    
    "default_socket": { 
        "port": 8080
    }, 
    "listen_socket": {
        "port": 0 
    },
    "fsroot": "/",
    "fsmappings": [
        {
            "concrete": "/",
            "virt": "/"
        }
    ],
    "env": {
        "myvar": "initial_value"
    },
    "instances": 1
}
EOF
    http_code=$(eval ${curl_cmd})
    curl_status=$?
    #expect to see something like the following :
    # {"ep":20125,"msg":"AddEndpoint","port":39187}
    # HTTP/1.1 200 OK
    # Content-Type: application/json
    # Date: Wed, 08 Nov 2023 03:44:41 GMT 
    # uWebSockets: 20
    # Content-Length: 46
    #
    if [[ ${verbose} == "yes" ]] ; then
        echo "${curl_cmd}" >&2
        cat ${curl_tmpdir}/http_request_body.json >&2 cat ${curl_tmpdir}/curl.header >&2
        cat ${curl_tmpdir}/curl.stdout >&2
        cat ${curl_tmpdir}/curl.stderr >&2
    fi
    if [[ ${curl_status} != 0 || ! ${http_code} =~ ^2[0-9][0-9]$ ]] ; then
        echo "[ERROR] unable to start isolate" >&2
        terminate_graalhost
        exit 1
    fi
    #isolate_port=$(cat ${curl_tmpdir}/curl.stdout | jq -a -e .port)

}


./launch-graalhost-container.sh

# Wait for graalhost to start running:
while [[ ! -S ${tmpdir}/graalhost.socket ]] ; do 
        sleep 0.1
done
echo "Graalhost is up"

load_aplication /scripts/apps/hello-world/helloworld

echo "Terminating GraalOS"
terminate_graalhost

sleep 1 #I need to wait for the graal os to change the logs permisions

# Validate the isolate output:
if ! grep --silent "Hello, World!" ${tmpdir}/isolate1.log ; then 
    echo "[ERROR] Unexpected isolate output" >&2
    exit 1
fi

# create a temporary directory to retain an execution log:
finaldir=$(mktemp -d ${CURRENT_DIR}/logs/graalos-$(whoami)-XXXXXXXX)
cp -r ${tmpdir}/* ${finaldir}
echo Folder containing the execution log: $finaldir