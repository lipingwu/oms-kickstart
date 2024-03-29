#!/bin/bash
#===============================================================================
# vim: softtabstop=4 shiftwidth=4 expandtab fenc=utf-8 
#===============================================================================
#
#          FILE: kickstart-kickstart.sh
#
#   DESCRIPTION: Kickstart OMS-Kickstart on a new VM/container
#
#          BUGS: https://github.com/IDCubed/oms-kickstart/issues
#        AUTHOR: luminous
#       LICENSE: ID3 MIT (X11)
#  ORGANIZATION: IDCubed.org
#       CREATED: 12/21/2013
#         NOTES: no effort (yet) towards POSIX compliance, just get it done
#===============================================================================
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
######
#
# here is the order of it all:
#
# 1) cat kick-ssh.py over ssh to a remote file, tweak permissions, and run it.
#    this will ensure we have ~/.ssh and expected files within
# 2) ensure our .id_rsa.pub is in the remote user's ~/.ssh/authorized_keys. we
#    can now ssh without having to use password auth
# 3) create directory ~/kickstart on remote host
# 4) rsync kickstart-oms.py and some configs to remote host
#generate some SSH keys on the host
# run kickstart in a tmux session, detached
#-------------------------------------------------------------------------------

USER_HOST=$1
REMOTE_HOME=$2
KICK_KICKSTART='kick-tmux.sh'
KICKSTART_SCRIPT='kickstart-oms.py'
RUN_KICKSTART='run-kickstart.sh'
CONFIGS='config'
PRIVATE_KEY='./config/keys/id_rsa'
PUBLIC_KEY='./config/keys/id_rsa.pub'
SSH_KEYS="$PRIVATE_KEY $PUBLIC_KEY"
UPLOAD_ME="$KICK_KICKSTART $RUN_KICKSTART $KICKSTART_SCRIPT $CONFIGS"
UPLOAD_TO="$REMOTE_HOME/kickstart"
PREFIX="### "

echo "$PREFIX Operate on Remote Host: $USER_HOST"
# FIRST SSH CONNECTION - figure out $HOME of the remote user
#export REMOTE_HOME=`ssh $USER_HOST 'echo $HOME'`
echo "$PREFIX \$HOME for $USER_HOST is: $REMOTE_HOME"

echo "$PREFIX create ~/.ssh if it does not exist"
ssh $USER_HOST "mkdir $REMOTE_HOME/.ssh"
# SECOND SSH CONNECTION
# use some blackmagic to keep this step in one SSH connection
#cat kick-ssh.py | ssh $USER_HOST "cat >> $KICK_SSH; chmod +x $KICK_SSH; $KICK_SSH"

echo "$PREFIX ensure local id_rsa.pub is in the remote user's ~/.ssh/authorized_keys"
rsync -vz ~/.ssh/id_rsa.pub  $USER_HOST:$REMOTE_HOME/.ssh/authorized_keys

#echo "$PREFIX update the password, of the user on the remote host"
#ssh $USER_HOST passwd

# if SSH keys exist, upload them
if  [ -f $PUBLIC_KEY ]  &&  [ -f $PRIVATE_KEY ]; then
  echo "$PREFIX upload SSH keys"
  rsync -avz $SSH_KEYS $USER_HOST:$REMOTE_HOME/.ssh/
else
  echo "$PREFIX no SSH keys to upload"
fi

ssh $USER_HOST "chmod -R o-rxw $REMOTE_HOME/.ssh && chmod -R g-rxw $REMOTE_HOME/.ssh"

echo "$PREFIX upload kickstart scripts and configs"
ssh $USER_HOST mkdir -p $UPLOAD_TO
rsync -avz $UPLOAD_ME $USER_HOST:$UPLOAD_TO

# confirm before we run kickstart..
read -p "ready to run kickstart! shall we continue? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ssh $USER_HOST $UPLOAD_TO/$KICK_KICKSTART
fi
