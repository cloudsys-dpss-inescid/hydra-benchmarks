#!/bin/bash

function DIR {
	echo "$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
}

if [[ -z "${ARGO_HOME}" ]]; then
	echo "ARGO_HOME is not defined. Existing..."
	exit 1
fi

function build_graalvisor_app {
	source $ARGO_HOME/lambda-manager/src/scripts/environment.sh
	cd build
	$JAVA_HOME/bin/native-image \
		--no-fallback \
		--enable-url-protocols=http \
		-cp libs/odd-even-1.0-all.jar\
		-DGraalVisorGuest=true \
		-Dcom.oracle.svm.graalvisor.libraryPath=resources/main/com.oracle.svm.graalvisor.headers \
		--initialize-at-run-time=com.oracle.svm.graalvisor.utils.JsonUtils \
		-H:ConfigurationFileDirectories=../ni-agent-config \
		-H:+ReportExceptionStackTraces \
		--shared \
		-H:Name=$1
}

./gradlew clean shadowJar assemble -Pglib='/graalvisor-lib/libs/graalvisor-lib-1.0-guest-before-substitution.jar'

(build_graalvisor_app oddeven_before_sub)

./gradlew shadowJar assemble -Pglib='/graalvisor-lib/libs/graalvisor-lib-1.0-guest-after-substitution.jar'

(build_graalvisor_app oddeven_after_sub)

#echo BENCHMARK_PATH=$(DIR)/build/libs/odd-even-1.0.jar
