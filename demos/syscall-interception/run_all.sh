#!/bin/bash

if [ $# -eq 0 ]; then
	echo "usage $0 iter_count"
	exit 1
fi

backup=backup/$(date +%Y.%m.%d.%H.%M.%S)
mkdir $backup

for d in */ ; do
	if [ ! -f $d/.testignore ]; then
		pushd $d > /dev/null
		find -type f -name '*.log' -delete
		./run.sh $@
		popd > /dev/null
		cp --parent $d/*.log $backup
	fi
done

