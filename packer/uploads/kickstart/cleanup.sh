#!/bin/sh
#
#

echo "-------------------------------------------------------------------------"
echo "Begin Image Clean Up!"

# Remove packages we don't want anymore, as well as stale dependencies
#apt-get -y remove linux-headers-$(uname -r)
apt-get -y autoremove
apt-get -y clean

# Remove SSH keys
echo "cleaning up SSH keys"
rm -rf /root/.ssh/id_rsa*
rm -rf /home/*/.ssh/id_rsa*

# Removing leftover leases and persistent rules
echo "cleaning up dhcp leases"
rm /var/lib/dhcp/*

# Make sure Udev doesn't block our network
echo "cleaning up udev rules"
rm /etc/udev/rules.d/70-persistent-net.rules
mkdir /etc/udev/rules.d/70-persistent-net.rules
rm -rf /dev/.udev/
rm /lib/udev/rules.d/75-persistent-net-generator.rules

echo "Adding a 2 sec delay to the interface up, to make the dhclient happy"
echo "pre-up sleep 2" >> /etc/network/interfaces

echo "Image Clean Up Complete!"
echo "-------------------------------------------------------------------------"
