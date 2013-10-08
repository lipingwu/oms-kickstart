#!/bin/sh
#===============================================================================
# vim: softtabstop=4 shiftwidth=4 expandtab fenc=utf-8 spell spelllang=en
#===============================================================================
#
#          FILE: kickstart-oms.sh
#
#   DESCRIPTION: Kickstart Open Mustard Seed on a new VM/container
#
#          BUGS: https://github.com/IDCubed/oms-kickstart/issues
#        AUTHOR: luminous
#       LICENSE: ID3 MIT (X11)
#  ORGANIZATION: IDCubed.org
#       CREATED: 06/09/2013
#         NOTES: no effort (yet) towards POSIX compliance
#                no support (yet) for other OS - Ubuntu 12.04 LTS only (sorry)
#                expects to run as root or via sudo
#                totally our first hack at this - not very intelligent
#===============================================================================
ScriptVersion="0.8.0"
ScriptName="kickstart-oms.sh"

HOSTNAME=`hostname -f`

# install salt-minon AND salt-master
wget -O - http://bootstrap.saltstack.org | sh 
stop salt-minion
stop salt-master

#------------------------------
# sprinkle some salt

# salt-minion config
cat > /etc/salt/minion << EOT
    file_roots:
      base:
        - /etc/salt/states
    pillar_roots:
      base:
        - /etc/salt/pillar
EOT


#------------------------------
# create a place for our salt states
mkdir -p /etc/salt/states/kick

# kick.start state
cat > /etc/salt/states/kick/start.sls << EOT
    kickstart:
      pkg.installed:
        - pkgs:
            - git
      git.latest:
        - name: https://github.com/IDCubed/oms-admin
        - target: /root/oms-admin
        - rev: master
        - require:
            - pkg: kickstart
      cmd.run:
        - name: sh /root/oms-admin/install.sh
        - require:
            - git: kickstart
EOT

# we should check to ensure salt actually installed correctly
salt-call --local state.sls kick.start
