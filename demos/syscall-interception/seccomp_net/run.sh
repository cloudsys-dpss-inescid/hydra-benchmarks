#!/bin/bash

DIR=$(cd $(dirname $0) && pwd)
source $DIR/../utils/shared.sh
BIN=$DIR/../build/bin/test_seccomp

if [ ! -f $BIN ]; then
	cd $DIR/..
	make
	cd -
fi

LOG=test_seccomp_mode_net.log
MODE="$BIN --mode-net"
run $@
