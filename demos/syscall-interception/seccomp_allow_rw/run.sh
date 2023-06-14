#!/bin/bash

DIR=$(cd $(dirname $0) && pwd)
source $DIR/../utils/shared.sh
BIN=$DIR/../build/bin/test_seccomp

if [ ! -f $BIN ]; then
	cd $DIR/..
	make
	cd -
fi

LOG=test_seccomp_mode_allow_rw.log
MODE="$BIN --mode-allow-rw"
run $@
