#!/bin/bash

APP=$BENCHMARKS_HOME/src/java/gv-shopcart/target/shopcart-0.3.6.jar
HOST=localhost
PORT=8080

function start_micronaut {
        $MODE java -jar $APP &> /dev/null &
        PID=$!
        while ! nc -z $HOST $PORT; do
                sleep 1
        done
        echo "Running ${LOG%.*}"
}

function stop_micronaut {
        kill -15 $PID
	while lsof -i :8080; do
		sleep .1
	done
}

function benchmark {
        ab -n $1 $HOST:$PORT/ > $DIR/$LOG
}

function run {
	start_micronaut
	benchmark $1
	stop_micronaut
	echo "Check results: $DIR/$LOG"
}

if [ $# -eq 0 ]; then
        echo "usage $0 iter_count"
        exit 1
fi
