## Introduction

To run the scripts, ensure that the global variable `GRAALOS_SDK_DIR`, or the same but local variable in the `launch-graalhost-container.sh` script, is defined and points to a directory containing the uncompressed GraalOS SDK. You can define the variable like this:

```sh
export GRAALOS_SDK_DIR="/home/claudiocorreia/graalos_work/graalos"
```

This directory contains a `Dockerfile` used to launch a container that will host Graal OS, running as a web service and accepting requests on a specified port (TBD). It also contains three scripts: `run-graalhost.sh`, `launch-graalhost-container.sh`, and `test-graalhost.sh`.

- **`run-graalhost.sh`**: Launches Graal OS as a web service on the local machine using the provided SDK.
- **`launch-graalhost-container.sh`**: Launches the Docker container and runs the `run-graalhost.sh` script inside the container.
- **`test-graalhost.sh`**: Uses the `launch-graalhost-container.sh` script to launch the Graal OS container and then sends an HTTP request using Curl to provide and execute a function. This script is useful for testing if everything is working correctly.

The execution logs are stored locally in the `logs/`, and costum applications are located in `apps`.