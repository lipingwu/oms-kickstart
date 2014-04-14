#!/bin/sh
#
#

echo "### ------------------------------------------------------"
echo "### clean up apt"

# Remove packages we don't want anymore, as well as stale dependencies
#apt-get -y remove linux-headers-$(uname -r)
apt-get -y autoremove
apt-get -y clean
