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

function request {
	cd $WORKLOADS
	rm -f shopcart-userids.txt
	wrk -t$1 -c$1 -d30s -R285 -s 1-create-shop-carts.lua http://$HOST:$PORT &> /dev/null
	wrk -t$1 -c$1 -d${2}s -R285 -s 1-create-shop-carts.lua http://$HOST:$PORT > $DIR/1-$LOG
	wrk -t$1 -c$1 -d60s -R714 -s 2-populate-shop-carts.lua http://$HOST:$PORT &> /dev/null
        wrk -t$1 -c$1 -d${2}s -R714 -s 2-populate-shop-carts.lua http://$HOST:$PORT > $DIR/2-$LOG
        wrk -t$1 -c$1 -d30s -R285 -s 3-read-shop-carts.lua http://$HOST:$PORT &> /dev/null
        wrk -t$1 -c$1 -d${2}s -R285 -s 3-read-shop-carts.lua http://$HOST:$PORT > $DIR/3-$LOG
	cd - > /dev/null
}

function tiny {
	request 1 10
}

function small {
	request 2 15
}

function medium {
	request 4 20
}

if [ $# -eq 0 ] || [[ ! $(type -t $1) == function ]]; then
        echo "usage $0 <tiny|small|medium>"
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
