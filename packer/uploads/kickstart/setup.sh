#!/bin/sh
#
#
echo ""
echo "### ------------------------------------------------------"
echo "### prepare the system to run OMS Kickstart"

echo "### copy SSH keys to /root/.ssh/ (for OMS system automa)"
mkdir /root/.ssh/
chmod 0700 /root/.ssh
cp -rp $HOME/.ssh/id_rsa* /root/.ssh/

echo "### ensure OMS has that root can SSH to localhost"
cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys

echo "### reset permissions on $HOME and /root/"
chmod -R o-rwx $HOME /root
chmod -R g-rwx $HOME /root
chown -R root:root /root

echo "### initial preparations complete!"
echo ""
