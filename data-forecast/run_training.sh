#!/bin/bash

IMAGE_NAME="timeseries-predictor-image"
CONTAINER_NAME="timeseries-predictor-container"
CURRENT_DIR=$(pwd)

docker build -t $IMAGE_NAME .

# Run the container in background/detached mode and give it a name
docker run -d --rm \
    --gpus all \
    --network host \
    -v "${CURRENT_DIR}:/data-forecast" \
    --name $CONTAINER_NAME \
    $IMAGE_NAME \
    sh -c "cd /data-forecast/predictor && ./run-training.sh"

docker logs -f $CONTAINER_NAME &> server.log &
