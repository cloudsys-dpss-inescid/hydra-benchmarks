#!/bin/bash

if [ $# -eq 0 ]; then
	echo "usage $0 iter_count"
	exit 1
fi

for d in */ ; do
	pushd $d > /dev/null
	if [ ! -f .testignore ]; then
		find -type f -name '*.log' -delete
		./run.sh $@
	fi
	popd > /dev/null
done
