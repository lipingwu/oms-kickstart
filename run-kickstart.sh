#!/bin/bash

# this is the command we run, when we 'run' kickstart-oms.py
# we need to create a script to run this stuff, so we can execute in tmux

cd ~/kickstart
python kickstart-oms.py -H -d -c config/release.yaml -c config/pillar/release.yaml
/bin/bash
