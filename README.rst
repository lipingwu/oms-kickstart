-------------
OMS-Kickstart
-------------

Kickstart OMS - to the cloud we go!


the script..
------------

even with its flaws, this is some serious awesome!

overall, this script completes three primary tasks:

  1) install and configure salt-minion on the host
  2) run state.high to apply some initial states
  3) run state.highstate to apply more advanced states

default config and state data is included in the script, so no
external config is necessary and the script can run by itself.

when run this way, kickstart-oms.py will apply a set of base
states that install minimal packages needed to clone the
oms-deploy repo and setup the host for a run of state.highstate.

state.highstate will update the system using the salt states and
pillar definitions from the oms-deploy repo.

kickstart-oms.py may be run with the following flags:

  -d  enables debug logging to share some helpful details
  -t  enables test (noop) mode, no actions will be taken
  -H  runs state.highstate after the host is setup with the
      base states
  -h  prints help messages
  -c  will let you provide a list of YAML-formatted configs
  -l  specify logfile to write to, when in debug mode

lastly, kickstart-oms.py will accept external configuration to
override the defaults embedded in the script. this is where
we get super awesome, as we are free to..

    A) provide any minion config we wish
    B) include any base states to apply

thus.. this script may be used to kickstart a host with an
arbitrary set of base states, then run state.highstate to
apply a second round of updates, allowing us to do pretty much
anything we want with salt.


example config
--------------

The following config is the YAML version of the defaults embedded in kickstart-oms.py::

    repos:
      states:
        oms-deploy:
          url: git@github.com:IDCubed/oms-deploy.git
          rev: qa-develop
          # specifies the directory within the repo (where to find states)
          copy_path: salt/states
      pillar:
        oms-deploy-pillar:
          url: git@github.com:IDCubed/oms-deploy.git
          rev: qa-develop
          copy_path: salt/pillar

    minion_config:
        path: /etc/salt/minion
        contents:
          master: 127.0.0.1
          file_roots:
            base:
              - /etc/salt/states
          pillar_roots:
            base:
              - /etc/salt/pillar
          file_client: local

    # base states applied after minion is installed
    kickstart_state:
      base_packages:
        pkg:
          - latest
          - names:
              - git
              - rsync
              - openssh-client
      ssh_config:
        file:
          - managed
          - name: /etc/ssh/ssh_config
          - contents: |
              Host *
              StrictHostKeyChecking no
              UserKnownHostsFile=/dev/null
          - require:
              - pkg: base_packages
      install_to:
        file:
          - directory
          - name: /etc/salt
          - makedirs: True
      salt_minion_files_roots:
        file:
          - directory
          - name: /etc/salt/states
          - makedirs: True
          - clean: True
          - require:
              - file: install_to
      salt_minion_pillar_roots:
        file:
          - directory
          - name: /etc/salt/pillar
          - makedirs: True
          - clean: True
          - require:
              - file: install_to


    # these are appended to the git repo states created on the fly
    # (for the repos included in this config)
    requirements:
      - pkg: base_packages
      - file: ssh_config
      - file: salt_minion_files_roots
      - file: salt_minion_pillar_roots


caveats
-------

 * requires Ubuntu 12.04 LTS until otherwise noted
 * completely brand new and under development - you have been warned!
