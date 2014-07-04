#!/bin/sh
#
# Copyright (C) 2014 the Institute for Institutional Innovation by Data
# Driven Design Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE INSTITUTE FOR INSTITUTIONAL
# INNOVATION BY DATA DRIVEN DESIGN INC. BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
# OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the names of the Institute for
# Institutional Innovation by Data Driven Design Inc. shall not be used in
# advertising or otherwise to promote the sale, use or other dealings
# in this Software without prior written authorization from the
# Institute for Institutional Innovation by Data Driven Design Inc.
#
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
