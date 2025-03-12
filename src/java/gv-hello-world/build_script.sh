#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

function run_hotspot {
        # Build.
        ./gradlew clean shadowJar assemble

        $JAVA_HOME/bin/java \
                -cp build/libs/hello-world-1.0-all.jar \
                com.hello_world.HelloWorld
}

function build_ni {
        # Build.
        ./gradlew clean shadowJar assemble

	cd build
	$JAVA_HOME/bin/native-image \
		--no-fallback \
		-H:-AllowVMInternalThreads \
		-cp libs/hello-world-1.0-all.jar \
		-H:+ReportExceptionStackTraces \
		$NI_BIN_OPTS \
		-H:Name=libhelloworld
}

function build_ni_standalone {
        # Build.
        ./gradlew clean shadowJar assemble

	NI_BIN_OPTS="com.hello_world.HelloWorld"
	build_ni
}

function build_ni_sharedlibrary {
        # Build.
        ./gradlew clean shadowJar assemble

	NI_BIN_OPTS="--shared"
	build_ni
}

function build_graalhost {
        # We need the parenthesis to create a subshell, since build-env-ec.sh exports env variables.
        (
        if [ -z "$GRAALOS_HOME" ]
        then
                echo "Please set GRAALOS_HOME first. It should point to a checkout of graalos sdk."
                exit 1
        fi
        source $GRAALOS_HOME/scripts/build-env-rc.sh

        ./gradlew clean shadowJar assemble -Pgraalhost
        NI_BIN_OPTS="com.hello_world.GraalHostMain"
        build_ni
        )
}

if [ -z "$ARGO_HOME" ]
then
        echo "Please set ARGO_HOME first. It should point to a checkout of github.com/graalvm/argo."
        exit 1
fi

if [ -z "$JAVA_HOME" ]
then
        echo "Please set JAVA_HOME first. It should be a GraalVM with native-image available."
        exit 1
fi

# Move into the script directory.
cd $DIR &> /dev/null

TARGET=$1
if [ ! -z "$TARGET" ]
then
        $TARGET
	exit 0
else
	read -p "Run benchmark on hotspot (y or Y, everything else as no)? " -n 1 -r
        echo # move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
                run_hotspot
                exit 0
        fi
	read -p "Build standalone Native Image (y or Y, everything else as no)? " -n 1 -r
        echo # move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
                build_ni_standalone
                exit 0
        fi
	read -p "Build shared library Native Image (y or Y, everything else as no)? " -n 1 -r
        echo # move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
                build_ni_sharedlibrary
                exit 0
        fi
	read -p "Build GraalOS image (y or Y, everything else as no)? " -n 1 -r
        echo # move to a new line
        if [[ $REPLY =~ ^[Yy]$ ]]
        then
                build_graalhost
                exit 0
        fi
fi
