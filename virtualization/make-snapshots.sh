#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

SNAPSHOTS_NUMBER=$1

SCRIPT_DIR=$DIR/../demos/firecracker-niuk

IP_ADDRESSES_STR=$(python3 $DIR/list-ips.py $SNAPSHOTS_NUMBER)
IP_ADDRESSES=(${IP_ADDRESSES_STR})

for ip in "${IP_ADDRESSES[@]}"
do
    echo "($ip) Starting vm..."
    $SCRIPT_DIR/start-vm.sh $ip &> $SCRIPT_DIR/start-vm-$ip.log &
    sleep 1
    echo "($ip) Configuring vm..."
    $SCRIPT_DIR/config-vm.sh $ip &> $SCRIPT_DIR/$ip/config-vm.log

    echo "($ip) Snapshotting vm..."
    $SCRIPT_DIR/snapshot-vm.sh $ip &> $SCRIPT_DIR/$ip/snapshot-vm.log

    echo "($ip) Stopping vm..."
    $SCRIPT_DIR/stop-vm.sh $ip &> $SCRIPT_DIR/$ip/stop-vm.log
done
