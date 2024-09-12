#!/bin/bash

IMAGE_NAME="timeseries-predictor-image"
#CONTAINER_NAME="timeseries-predictor-container"
CONTAINER_NAME=$2
CURRENT_DIR=$(pwd)
MODELS_DIR="../predictor/custom_autogluon/autogluon_models"

if [ -z "$CONTAINER_NAME" ]
then
    CONTAINER_NAME="timeseries-predictor-container"
fi

# check if there are trained models
if [ ! -d "$MODELS_DIR" ]; then
  echo "$MODELS_DIR does not exist."
  mkdir $MODELS_DIR
fi

if [ -z "$(ls -A "$MODELS_DIR")" ]; then
    echo "No trained models found, it will train now."
    ./run_training.sh
fi

docker build -t $IMAGE_NAME .

# Run the container in background/detached mode and give it a name
docker run -d --rm \
    --gpus all \
    --network host \
    -v "${CURRENT_DIR}/../../data-forecast:/data-forecast" \
    -v "${CURRENT_DIR}/../../azure-dataset:/azure-dataset" \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v $(which docker):/usr/bin/docker \
    --name $CONTAINER_NAME \
    -w "/data-forecast/service" \
    $IMAGE_NAME \
    python3 "http_server.py" $1 #I assume the first argument is the server port

docker logs -f $CONTAINER_NAME &> "debug/server-$CONTAINER_NAME.log" &
