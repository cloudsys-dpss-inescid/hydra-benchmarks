#!/bin/bash

APP=$BENCHMARKS_HOME/src/java/gv-shopcart/target/shopcart-0.3.6.jar
HOST=localhost
PORT=8080

function start_micronaut {
        $@ java -jar $APP &> /dev/null &
        PID=$!
        while ! nc -z $HOST $PORT; do
                sleep 1
        done
        echo "Micronaut is running"
}

function stop_micronaut {
        kill -15 $PID
}

function benchmark {
        ab -n $1 $HOST:$PORT/ > $DIR/ab.log
}

function run {
	start_micronaut $1
	benchmark $2
	stop_micronaut
	echo "Check results: $DIR/ab.log"
}

if [ $# -eq 0 ]; then
        echo "usage $0 iter_count"
        exit 1
fi
