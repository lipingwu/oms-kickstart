#!/usr/bin/env bash
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
