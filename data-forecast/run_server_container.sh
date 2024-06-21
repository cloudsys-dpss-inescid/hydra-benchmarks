#!/bin/bash

IMAGE_NAME="timeseries-predictor-image"

docker build -t $IMAGE_NAME .

# replace the -it with -d to run the service in background/detached 
docker run -it --rm \
    --network host \
    -v ~/work/hydra/benchmarks/data-forecast:/data-forecast \
    $IMAGE_NAME

