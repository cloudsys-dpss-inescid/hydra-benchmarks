#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

GRAALVISOR_HOME=$ARGO_HOME/graalvisor

JAVA_AGENT="$JAVASSIST_HOME/target/JavassistWrapper-1.0-jar-with-dependencies.jar"

JNI_INCLUDE="-I$DEF_JAVA_HOME/include -I$DEF_JAVA_HOME/include/linux"
ERIM_INCLUDE="-I$ERIM_HOME/src/erim -I$ERIM_HOME/src/common"

CFLAGS="-Wall -g -fPIC -shared $JNI_INCLUDE"
CFLAGS_PROC="-Wall -g -fPIC $JNI_INCLUDE"
SFLAGS="$CFLAGS -O0 -fno-inline $ERIM_INCLUDE -I$GRAALVISOR_HOME/src/main/c/memisolation/src"
SFLAGS_PROC="$CFLAGS_PROC -O0 -fno-inline $ERIM_INCLUDE -I$GRAALVISOR_HOME/src/main/c/memisolation/src"

BENCHMARK_NAME="nativemsg"
SNIPPETS_DIR="$DIR/build/snippets"
SOURCE_CODE="$DIR/src/main/c/MessageJNI.c"

function run_hotspot {
	rm -rf config-dir
	CLASS_PATH="classes/java/main"

	cd build
	export LD_LIBRARY_PATH=$GRAALVISOR_HOME/build/libs:libs:$LD_LIBRARY_PATH
	$JAVA_HOME/bin/java \
			-Djava.awt.headless=true \
			-agentlib:native-image-agent=config-output-dir=config-dir/ \
			-cp $CLASS_PATH:libs/native-msg-1.0-all.jar \
			-Djava.library.path=$LD_LIBRARY_PATH \
			com.jni.MessageJNI
}

function build_ni {
	CLASS_PATH="classes/java/main"

	cd build
	export LD_LIBRARY_PATH=$GRAALVISOR_HOME/build/libs:libs:$LD_LIBRARY_PATH
	$JAVA_HOME/bin/native-image \
			--no-fallback \
			-cp $CLASS_PATH:libs/native-msg-1.0-all.jar:$GRAALVISOR_HOME-lib/build/libs/graalvisor-lib-1.0-guest.jar \
			-DGraalVisorGuest=true \
			-Djava.library.path=$LD_LIBRARY_PATH \
			-Dcom.oracle.svm.graalvisor.libraryPath=$GRAALVISOR_HOME-lib/build/resources/main/com.oracle.svm.graalvisor.headers \
			--initialize-at-run-time=com.oracle.svm.graalvisor.utils.JsonUtils \
			-H:ConfigurationFileDirectories=../ni-agent-config \
			-H:+ReportExceptionStackTraces \
			$NI_BIN_OPTS \
			-H:Name=lib$BENCHMARK_NAME
}

function build_ni_standalone {
	NI_BIN_OPTS="com.jni.MessageJNI"
	build_ni
}

function build_ni_sharedlibrary {
	NI_BIN_OPTS="--shared"
	build_ni
}

function build_java_agent {
	bash $JAVASSIST_HOME/build.sh
}

function build_native_library {
	gcc $CFLAGS -o $GRAALVISOR_HOME/build/libs/lib$BENCHMARK_NAME-jni.so $SOURCE_CODE
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

if [ -z "$JAVASSIST_HOME" ]
then
	echo "Please set JAVASSIST_HOME first."
	exit 1
fi

# Build graalvisor lib.
bash $ARGO_HOME/graalvisor-lib/build.sh

# Build java agent.
build_java_agent

# Move into the script directory.
cd $DIR &> /dev/null

# Build application.
./gradlew clean shadowJar assemble

# Build native lib.
build_native_library

TARGET=$1
if [ ! -z "$TARGET" ]
then
	$TARGET
exit 0
else
	build_ni_sharedlibrary
	exit 0
fi
