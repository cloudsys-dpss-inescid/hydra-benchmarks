#!/bin/bash

IMAGE_NAME="timeseries-predictor-image"
CONTAINER_NAME="timeseries-predictor-container"
CURRENT_DIR=$(pwd)
MODELS_DIR="../predictor/autogluon_models"

# check if there are trained models
if [ -d "$MODELS_DIR" ] && [ -z "$(ls -A "$MODELS_DIR")" ]; then
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
    --name $CONTAINER_NAME \
    $IMAGE_NAME \
    python3 "/data-forecast/service/http_server.py"

docker logs -f $CONTAINER_NAME &> debug/server.log &
