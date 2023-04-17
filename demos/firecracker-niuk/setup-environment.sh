#!/bin/bash

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

cd $DIR &> /dev/null

ARGO_HOME="$DIR"/../../../argo

echo "Checking if you have firecracker..."
if [ ! -f release-v1.1.0-x86_64/firecracker-v1.1.0-x86_64 ];
then
    wget https://github.com/firecracker-microvm/firecracker/releases/download/v1.1.0/firecracker-v1.1.0-x86_64.tgz
    tar -vzxf firecracker-v1.1.0-x86_64.tgz
    rm firecracker-v1.1.0-x86_64.tgz
fi
echo "Checking if you have firecracker... done!"

echo "Checking if you have a linux kernel image..."
if [ ! -f hello-vmlinux.bin ];
then
    cp "$ARGO_HOME"/resources/hello-vmlinux.bin ./hello-vmlinux.bin
fi
echo "Checking if you have a linux kernel image... done!"

echo "Checking if you have a base rootfs..."
if [ ! -f hello-rootfs.ext4 ];
then
    cp "$ARGO_HOME"/graalvisor/build/native-image/polyglot-proxy.img ./hello-rootfs.ext4
fi
echo "Checking if you have a base rootfs... done!"

cd - &> /dev/null
