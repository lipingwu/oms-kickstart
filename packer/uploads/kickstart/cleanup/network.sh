#!/bin/sh

echo ""
echo "### ------------------------------------------------------"
echo "### cleanup network configuration (dhcp/udev)"

# Removing leftover leases and persistent rules
echo "### cleaning up dhcp leases"
rm /var/lib/dhcp/*

# Make sure Udev doesn't block our network
echo "### cleaning up udev rules"
rm -rf /etc/udev/rules.d/70-persistent-net.rules
mkdir /etc/udev/rules.d/70-persistent-net.rules
rm -rf /dev/.udev/

# reset default network config
#echo "### Reset /etc/network/interfaces"
#echo "# auto-generated /etc/network/interfaces" > /etc/network/interfaces
#echo "# OMS VM Image Automation with Packer" >> /etc/network/interfaces
#echo "auto lo" >> /etc/network/interfaces
#echo "iface lo inet loopback" >> /etc/network/interfaces

#echo "### Add a 2 sec delay to the interface up, keeps dhclient happy"
#echo "pre-up sleep 2" >> /etc/network/interfaces
#echo ""
