#!/bin/bash

IMAGE_NAME="timeseries-predictor-image"
CONTAINER_NAME="timeseries-predictor-container"
CURRENT_DIR=$(pwd)
DATASET_DIR="../../azure-dataset/input"

# check if the Azure dataset is found localy, other wise download it
if [ -d "$DATASET_DIR" ] && [ -z "$(find "$DATASET_DIR" -type f | grep -v '\.gitignore')" ]; then
    echo "Azure dataset not found, it will downdload it now."
    ./../../azure-dataset/download_dataset.sh 
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
    sh -c "cd /data-forecast/predictor/custom_autogluon && ./run-training.sh"

docker logs -f $CONTAINER_NAME &> debug/server.log &

echo "training...."
docker wait $CONTAINER_NAME
echo "training finished!"
