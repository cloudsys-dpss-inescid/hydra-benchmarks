#!/bin/bash

IMAGE_NAME="graalos-image"
CONTAINER_NAME="graalos-container"
CURRENT_DIR=$(pwd)
#GRAALOS_SDK_DIR="/home/claudiocorreia/graalos_work/graalos"

if [ -z "$GRAALOS_SDK_DIR" ]
then
    echo "Please set GRAALOS_SDK_DIR first. It should point to directory conainting an unziped version of the Graal IS SDK."
    exit 1
fi

logsdir=${CURRENT_DIR}/logs/graalos-last
rm -r ${logsdir}/* &>/dev/null 
mkdir ${logsdir} &>/dev/null 

echo hello
docker build -t $IMAGE_NAME .

# Run the container in background/detached mode
docker run -t -d --rm \
    --network host \
    --name $CONTAINER_NAME \
    -v "${GRAALOS_SDK_DIR}:/graalos" \
    -v "${CURRENT_DIR}:/scripts" \
    -e GRAALOS_SDK_DIR="/graalos" \
    $IMAGE_NAME \
    ./run-graalhost.sh


