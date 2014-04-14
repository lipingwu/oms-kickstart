#!/bin/sh
#

echo ""
echo "### ------------------------------------------------------"
echo "### removing SSH keys from /root/ and /home/*"
rm -rf /root/.ssh/id_rsa*
rm -rf /home/*/.ssh/id_rsa*
echo ""
