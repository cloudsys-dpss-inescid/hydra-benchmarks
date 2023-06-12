#!/bin/bash

DIR=$(cd $(dirname $0) && pwd)
source $DIR/../utils/shared.sh
BIN=$DIR/../build/bin/test_seccomp

if [ ! -f $BIN ]; then
	cd $DIR/..
	make
	cd -
fi

# run mode strict
LOG=test_seccomp_mode_strict.log
MODE="$BIN --mode-strict"
run $@

# run mode fs
LOG=test_seccomp_mode_fs.log
MODE="$BIN --mode-fs"
run $@
