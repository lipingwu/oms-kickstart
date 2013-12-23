#!/usr/bin/env bash

echo ""
echo "------------------------------------------------------"
echo "### install virtualbox guest additions"

# create a temporary working directory
mkdir /tmp/virtualbox
# packer creates this version file for us
VERSION=$(cat $HOME/.vbox_version)
# make the virtualbox guest additions iso available
mount -o loop $HOME/VBoxGuestAdditions_$VERSION.iso /tmp/virtualbox
# run the guest additions installer
sh /tmp/virtualbox/VBoxLinuxAdditions.run -- --force

# clean up! close and remove the iso and working directory
umount /tmp/virtualbox
rmdir /tmp/virtualbox
rm $HOME/VBoxGuestAdditions_$VERSION.iso

echo "### virtualbox guest additions complete!"
echo ""
