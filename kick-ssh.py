#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2013 the Institute for Institutional Innovation by Data
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
# NONINFRINGEMENT. IN NO EVENT SHALL THE MASSACHUSETTS INSTITUTE OF
# TECHNOLOGY AND THE INSTITUTE FOR INSTITUTIONAL INNOVATION BY DATA
# DRIVEN DESIGN INC. BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the names of the Institute for
# Institutional Innovation by Data Driven Design Inc. shall not be used in
# advertising or otherwise to promote the sale, use or other dealings
# in this Software without prior written authorization from the
# Institute for Institutional Innovation by Data Driven Design Inc.


'''
Kickstart SSH Keys, if needed
'''

import os
import subprocess

home = os.path.expanduser("~")
dot_ssh = os.path.join(home, '.ssh')
id_rsa = os.path.join(dot_ssh, 'id_rsa')
authorized_keys = os.path.join(dot_ssh, 'authorized_keys')

# create .ssh if it doesn't exist
if not os.path.exists(dot_ssh):
   os.mkdir(dot_ssh, 0700)

# ensure SOMETHING is there for an authorized_keys, if even empty
if not os.path.exists(authorized_keys):
   subprocess.check_call(('touch', authorized_keys)) 

# reset group/world permissions for .ssh/*
subprocess.check_call(('chmod', '-R', 'g-rxw', dot_ssh))
subprocess.check_call(('chmod', '-R', 'o-rxw', dot_ssh))
