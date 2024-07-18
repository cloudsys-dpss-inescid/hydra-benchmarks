#!/bin/bash

IMAGE_NAME="timeseries-predictor-image"
#CONTAINER_NAME="timeseries-predictor-container"
CONTAINER_NAME=$2
CURRENT_DIR=$(pwd)
MODELS_DIR="../predictor/autogluon_models"

if [ -z "$CONTAINER_NAME" ]
then
    CONTAINER_NAME="timeseries-predictor-container"
fi



docker build -t $IMAGE_NAME .

# Run the container in background/detached mode and give it a name
docker run -it --rm \
    --gpus all \
    --network host \
    -v "${CURRENT_DIR}/../../data-forecast:/data-forecast" \
    -v "${CURRENT_DIR}/../../azure-dataset:/azure-dataset" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(which docker):/usr/bin/docker \
    --name $CONTAINER_NAME \
    $IMAGE_NAME 
    #\
    #python3 "/data-forecast/service/debug.py"
