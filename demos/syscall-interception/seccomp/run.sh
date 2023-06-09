#!/bin/bash

DIR=$(cd $(dirname $0) && pwd)
BIN=$DIR/../build/bin/test_seccomp
source $DIR/../utils/shared.sh
run $BIN $1
