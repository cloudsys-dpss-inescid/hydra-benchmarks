#!/bin/bash

GRAALOS_SDK_DIR="/home/claudiocorreia/graalos_work/graalos"

if [ -z "$GRAALOS_SDK_DIR" ]
then
    echo "Please set GRAALOS_SDK_DIR first. It should point to directory conainting an unziped version of the Graal IS SDK."
    exit 1
fi




















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


echo "starting graalhost"
# start graalhost as a single process containing the hub & a single visor:
${GRAALOS_SDK_DIR}/graalhost/graalhost --verbose \
          --port=uds@${tmpdir}/graalhost.socket \
          --seccomp 2 \
          --hub \
          --webserver \
          --internal_visor \
          --add_visors=1 \
          --log_to=file \
          --visorcalloutput=visorcalloutput.txt \
          --musl_path=${GRAALOS_HOME}/graalhost/libc.so \
          --ephemeral_dir=${tmpdir} \
          --write_pid=${tmpdir}/graalhost.pid \
           >${tmpdir}/graalhost.stdout \
           2>${tmpdir}/graalhost.stderr &
echo "graalhost"

# get the Unix domain socket path to the hub (aka management
# interface):
hub_port=${tmpdir}/graalhost.socket

# Wait for graalhost to start running:
while [[ ! -S ${tmpdir}/graalhost.socket ]] ; do 
        sleep 0.1
done
graalhost_pid=$(<${tmpdir}/graalhost.pid)
echo "graalhost up"

# The graalos management interface expects you to define an end point 
# ID, which is unique to this instance of the hub:
epid=2001

# The isolate to run:
ISOLATE=${CURRENT_DIR}/apps/hello-world/helloworld

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
echo "first curl"
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
isolate_port=$(cat ${curl_tmpdir}/curl.stdout | jq -a -e .port)

terminate_graalhost

# Validate the isolate output:
if ! grep --silent "Hello, World!" ${tmpdir}/isolate1.log ; then 
    echo "[ERROR] Unexpected isolate output" >&2
    exit 1
fi    