#!/bin/bash
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

PREFIX="### "
# ensure we have tmux available to us before we do anything else
echo "$PREFIX ensure tmux is installed and available before we do anything"
apt-get update
apt-get install -y tmux
# make sure there are no other sessions to get in the way
echo "$PREFIX in-case there is an open tmux session, try to kill it"
echo "$PREFIX this may error out, but that is ok"
tmux kill-session -t kickstart
echo "$PREFIX starting a new tmux session, name it kickstart"
tmux new-session -d -s kickstart
echo "$PREFIX creating a new window in the session and run kickstart"
tmux new-window -n kickstart -t kickstart '/bin/bash -c ~/kickstart/run-kickstart.sh'
