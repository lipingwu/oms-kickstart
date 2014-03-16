#!/bin/bash

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
