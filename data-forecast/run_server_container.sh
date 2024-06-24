#!/bin/bash

IMAGE_NAME="timeseries-predictor-image"
CURRENT_DIR=$(pwd)

docker build -t $IMAGE_NAME .

# replace the -it with -d to run the service in background/detached 
docker run -it --rm \
    --network host \
    -v "${CURRENT_DIR}:/data-forecast" \
    $IMAGE_NAME

