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
	echo "Check results: $DIR/$LOG"
}

function run {
	start_micronaut
#	benchmark $1
	$1
	stop_micronaut
}

function small {
	cd $WORKLOADS
	rm shopcart-userids.txt
	wrk -t2 -c2 -d30s -R285 -s 1-create-shop-carts.lua http://$HOST:$PORT &> /dev/null
	wrk -t2 -c2 -d15s -R285 -s 1-create-shop-carts.lua http://$HOST:$PORT > $DIR/1-small-$LOG
	wrk -t2 -c2 -d60s -R714 -s 2-populate-shop-carts.lua http://$HOST:$PORT &> /dev/null
	wrk -t2 -c2 -d15s -R714 -s 2-populate-shop-carts.lua http://$HOST:$PORT > $DIR/2-small-$LOG
	wrk -t2 -c2 -d30s -R285 -s 3-read-shop-carts.lua http://$HOST:$PORT &> /dev/null
	wrk -t2 -c2 -d15s -R285 -s 3-read-shop-carts.lua http://$HOST:$PORT > $DIR/3-small-$LOG
	cd - > /dev/null
}

function medium {
	cd $WORKLOADS
        rm shopcart-userids.txt
        wrk -t4 -c4 -d30s -R285 -s 1-create-shop-carts.lua http://$HOST:$PORT &> /dev/null
	wrk -t4 -c4 -d20s -R285 -s 1-create-shop-carts.lua http://$HOST:$PORT > $DIR/1-medium-$LOG
        wrk -t4 -c4 -d60s -R714 -s 2-populate-shop-carts.lua http://$HOST:$PORT &> /dev/null
	wrk -t4 -c4 -d20s -R714 -s 2-populate-shop-carts.lua http://$HOST:$PORT > $DIR/2-medium-$LOG
        wrk -t4 -c4 -d30s -R285 -s 3-read-shop-carts.lua http://$HOST:$PORT &> /dev/null
	wrk -t4 -c4 -d20s -R285 -s 3-read-shop-carts.lua http://$HOST:$PORT > $DIR/3-medium-$LOG
        cd - > /dev/null
}

if [ $# -eq 0 ] || [[ ! $(type -t $1) == function ]]; then
        echo "usage $0 <small|medium>"
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
