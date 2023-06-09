#!/bin/bash

DIR=$(cd $(dirname $0) && pwd)
source $DIR/../utils/shared.sh
run "strace -f" $1
