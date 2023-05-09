#!/bin/bash

# This script builds the benchmark with argo-builder container.
# The benchmark name is specified in the first parameter.
#
# Example usage: build_benchmark.sh gv-hello-world
#
# This script assumes that the user has the argo-builder container
# locally. It can be built by running $ARGO_HOME/graalvisor/make_builder_image.sh

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

if [ -z "$ARGO_HOME" ]
then
    echo "Please set ARGO_HOME first. It should point to a checkout of github.com/graalvm/argo."
    exit 1
fi

if [ -z "$JAVA_HOME" ]
then
    echo "Please set JAVA_HOME first. It should be a GraalVM with native-image available."
    exit 1
fi

BENCHMARK_NAME=$1
if [ -z "$BENCHMARK_NAME" ]
then
    echo "Benchmark name is not present."
    exit 1
fi

BENCHMARK_HOME=$DIR/$BENCHMARK_NAME

docker run -it -v $JAVA_HOME:/jvm -v $ARGO_HOME:/argo -v $BENCHMARK_HOME:/benchmark-home -w /benchmark-home --rm argo-builder /benchmark-home/build_script.sh
sudo chown -R $USER:$USER $BENCHMARK_HOME/build
