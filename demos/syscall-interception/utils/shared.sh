#!/bin/bash

APP=$BENCHMARKS_HOME/src/java/gv-shopcart/target/shopcart-0.3.6.jar
WORKLOADS=$DIR/../workloads
HOST=localhost
PORT=8080

function start_micronaut {
        $MODE java -jar $APP &> /dev/null &
        PID=$!
        while ! nc -z $HOST $PORT; do
                sleep 1
        done
        echo "Running $(basename $DIR)"
}

function stop_micronaut {
        kill -15 $PID
	while lsof -i :8080; do
		sleep .1
	done
}

function benchmark {
	# warmup
	ab -n 1000 -T 'application/json' -p $WORKLOADS/create-shop-cart.json localhost:8080/ &> /dev/null
	ab -n 1000 localhost:8080$(cat $WORKLOADS/cart.id) &> /dev/null

	for i in {1..1}
	do
		output=$DIR/post.log
		ab -n $1 -T 'application/json' -p $WORKLOADS/create-shop-cart.json localhost:8080/ > $output
		echo "Check results: $output"
		output=$DIR/get.log
		ab -n $1 localhost:8080/$(cat $WORKLOADS/cart.id) > $output
		echo "Check results: $output"
	done
}

function run {
	start_micronaut
	benchmark $1
	stop_micronaut
}

if [ $# -eq 0 ]; then
	echo "usage $0 iter_count"
	exit 1
fi

if [ -z $BENCHMARKS_HOME ]; then
	echo "Please set BENCHMARKS_HOME first"
        exit 1
fi

if [ ! -f $APP ]; then
	echo "Please build shopcart first"
	exit 1
fi
