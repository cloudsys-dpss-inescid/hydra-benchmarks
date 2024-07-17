#!/bin/bash

if [ -z "$GRAALOS_SDK_DIR" ]
then
    echo "Please set GRAALOS_SDK_DIR first. It should point to directory conainting an unziped version of the Graal IS SDK."
    exit 1
fi

CURRENT_DIR=$(pwd)

source ${GRAALOS_SDK_DIR}/scripts/build-env-rc.sh

# create a temporary directory to retain an execution log:
tmpdir=${CURRENT_DIR}/logs/graalos-last

declare -i curl_counter=0
#verbose="yes"

function prepare_graalos_resources() {

    # get the Unix domain socket path to the hub (aka management
    # interface):
    hub_port=${tmpdir}/graalhost.socket

    # Wait for graalhost to start running:
    while [[ ! -S ${tmpdir}/graalhost.socket ]] ; do 
            sleep 0.1
    done
    graalhost_pid=$(<${tmpdir}/graalhost.pid)
    echo "graalhost is up"

    chmod -R 777 $tmpdir #change permition of all files that where created unitl now

}

prepare_graalos_resources &

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
           2>${tmpdir}/graalhost.stderr 
echo "graalhost"

chmod -R 777 $tmpdir #change permition of all files that where created unitl now




