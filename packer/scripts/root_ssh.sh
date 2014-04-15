#!/bin/sh


# setup root with the SSH key dropped into the VM
mkdir /root/.ssh
mv /home/oms/.ssh/id_rsa* /root/.ssh/
chmod 0700 /root/.ssh
chmod 0600 /root/.ssh/*

# copy kickstart scripts to /root for convenience
cp -r /home/oms/oms-kickstarter /root/
