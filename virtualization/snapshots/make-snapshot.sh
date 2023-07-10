#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

function make_snapshot {
    image_name=$1

    echo "($ID) Starting vm..."
    $DIR/start-vm.sh $ID $IP $image_name &> $DIR/$image_name/start-vm-$ID.log &
    sleep 1
    echo "($ID) Configuring vm..."
    $DIR/config-vm.sh $ID $IP $image_name &> $DIR/$image_name/config-vm-$ID.log

    echo "($ID) Snapshotting vm..."
    $DIR/snapshot-vm.sh $ID $IP $image_name &> $DIR/$image_name/snapshot-vm-$ID.log

    echo "($ID) Stopping vm..."
    $DIR/stop-vm.sh $ID $IP $image_name &> $DIR/$image_name/stop-vm-$ID.log
}

IMAGE=$1

ID=3
IP=172.18.0.3

if [ -z "$IMAGE" ]; then
    for image_name in graalvisor hotspot hotspot-agent java-openwhisk; do
        make_snapshot $image_name
    done
else
    make_snapshot $IMAGE
fi
