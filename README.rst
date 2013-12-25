-------------
OMS-Kickstart
-------------

Kickstart OMS - to the cloud we go!

This repository contains scripts and configuration files to kickstart a new host
with arbitrary bootstrapping and system provisioning.

The configuration included will kickstart the bootstrap process used in the Open
Mustard Seed project, but the kickstart framework will accept an arbitrary
concept of bootstrapping as expressed through Salt States.

In other words: the tools included in this repository will enable you to easily
run arbitrary Salt States and Modules to provision a new (Ubuntu) host.


Utilities Available
-------------------

``kickstart-oms.py``: The primary script for this whole kickstart process, acting
as the execution framework to setup the Host as a salt-minion for use in
controlling the Host through salt. Arbitrary configuration may be provided through
simple YAML files (one or more). Both Salt state definitions as well as Salt
pillar configuration dictionaries may be included in either the YAML config
provided, in one or more git repositories, or both. Wow!

``kickstart-kickstart.sh``: Helper script to ease kickstarting ``kickstart-oms.py``
on a new host, via SSH. Eg, from a separate development host, this script can be
used to automate the few (minor) manual steps to setup SSH keys, upload the
scripts and config files needed, etc.

``kick-tmux.sh``: Helper script to ease running the kickstart python script in a
tmux session. this will first try to kill a session with the name ``kickstart``,
then create a new session with this name, create a new window and execute the
``run-kickstart.sh`` script.

``run-kickstart.sh``: Helper script to wrap up running ``kickstart-oms.py`` with
all the arguments you desire (simplify the setup and prevents tmux from yelling
at us).


Initial Setup
-------------

If on a Unix-like OS (ie NOT Windows), getting started is easy. If on Windows,
you might want to get a Unix-like OS on a VM and work from there. Though, if the
host you will kickstart *is* going to be that system away from Windows, upload
the oms-kickstart repo to that host.

* Download the oms-kickstart repository to your local development system
* create SSH keypair with ``ssh-keygen -f oms-kickstart/config/keys``, and
  ensure the public key is associated with your git account if you need it. If
  deploying OMS without modification, you will need to do this for your github
  account.
* upload the scripts, configs, and SSH keypair to the host you will kickstart,
  or see the helper scripts detailed later in this document.


kickstart-oms.py
----------------

This is the primary script to use in the kickstart process, everything else is
just a helper.


intended use
~~~~~~~~~~~~

overall, this script completes four primary tasks:

1) install and configure salt-minion on the host
2) run ``state.high`` to apply some initial states (bootstrap to get more code)
3) run ``state.highstate`` to apply more advanced states
4) if specified, run additional salt modules/functions

default config and state data is included in the script, so no external config
is necessary and the script can run by itself.

when run this way, ``kickstart-oms.py`` will apply a set of base states that
install minimal packages needed to clone the oms-deploy repo and setup the host
for a run of ``state.highstate``.

``state.highstate`` will update the system using the salt states and pillar
definitions from the oms-deploy repo.


control flags
~~~~~~~~~~~~~

``kickstart-oms.py`` may be run with the following flags:

-d  enables debug logging to share some helpful details
-t  enables test (noop) mode, no actions will be taken
-H  runs ``state.highstate`` after the host is setup with the base states
-h  prints help messages
-c  will let you provide a list of YAML-formatted configs
-l  specify logfile to write to, when in debug mode

lastly, ``kickstart-oms.py`` will accept external configuration to override the
defaults embedded in the script. this is where we get super awesome, as we are
free to..

1) provide any minion config we wish
2) include any base states to apply
3) include a list of additional salt modules to execute

thus.. this script may be used to kickstart a host with an arbitrary set of base
states, then run ``state.highstate`` to apply a second round of updates, and
finally, execute additionalallowing us to do pretty much anything we want with
salt.


requirements
~~~~~~~~~~~~

* run on Ubuntu 12.04 LTS - no other system is currently supported.
* expects that the user has created an SSH key pair for use with cloning
  any git repositories, else git repos ought to be public.
* run as root, or with ``sudo``.
* use tmux so you don't run into problems getting disconnected.


use tmux
~~~~~~~~

Given the details of how SSH and long-running processes work, it is best to run
the kickstart from within an instance of tmux, so first start tmux with:
``tmux``. A full tmux tutorial is beyond the scope of this document, but here
are a few helpful details:

* If you lose your connection to the VM, you can simply login again and run
  ``tmux att``.
* Commands are prefixed with a modifier, ``Ctrl-b`` by default.
* You can separate from a running instance, to reattach later, with:
  ``Ctrl-b,d``.
* Create a new window with ``Ctrl-b,c`` (*create*), and switch between with
  ``p``, ``n``, and ``l``, for *previous*, *next* and *last*, respectively.
* Exit tmux by closing all open windows (exit the shell with ``exit``).


default OMS deployment
~~~~~~~~~~~~~~~~~~~~~~

assuming you are starting with a new VM, and are in an instance of tmux..

* create an ssh key with ssh-keygen, saved to ``~/.ssh/id_rsa``
* add the pub key to your github account, or whereever the git repos are stored
* copy `the kickstart script`_ and `the external config`_ to the VM
* run the script with: ``python kickstart-oms.py -H -c config/example.yaml``
* go grab a fresh beverage and/or entertain yourself for 10 minutes or so
* once complete, the VM ought to be completely setup and ready for either
  additional webapp deployments or for you to start hacking away! you will find
  all OMS source checked out to ``/var/oms/src/``

.. _the kickstart script: https://github.com/IDCubed/oms-kickstart/blob/qa-develop/kickstart-oms.py
.. _the external config: https://github.com/IDCubed/oms-kickstart/blob/qa-develop/example.yaml


other uses
~~~~~~~~~~

by using a custom external config (detailed in the next section), you can define
arbitrary states, a custom minion config, and even run addional salt modules at
the end of the initial kickstart.

omitting the ``-H`` flag will have the script skip running ``state.highstate``
after the initial run of ``state.high``.

use the ``-t`` flag if you would like to test the run first, and enable debug
mode with ``-d`` to see printouts of the states and configs that will be used.

additional salt modules may be specified with the ``post_kick`` config key, the
script will run each of these listed after ``state.high/highstate``.


stack the configs
~~~~~~~~~~~~~~~~~

it is possible to provide the config to oms-kickstart as a set of files, just
include a separate ``-c file.yaml`` for each file to include:

.. code::

   python kickstart-oms.py -H -d -c config/qa.yaml -c config/pillar.yaml


.. note::

   the keys from each file are merged together into one dictionary, duplicate
   keys will step on existing keys when merged.


yaml config
-----------

if you would like to build a custom config, instead of using the defaults
embedded in the script, you will need to include definitions for the following
config keys:

* ``repos``: a dictionary with two subkeys..
   - ``states``: dictionary describing the git repos to clone/checkout for
     states. multiple repos are supported. at least one is required.
   - ``pillar``: single-item dictionary describing the git repo to use for
     pillar data. only one repo may be used. this key is optional.

* ``pillar``: a dictionary of pillar config to write to the new minion installed,
  as top.sls and bootstrap.sls. this key is optional, and may even be used in
  conjunction with the pillar from git repos, eg ``[repos][pillar]``, though do
  be careful with what files and keys step on what. this must be pure YAML, no
  jinja/etc as with normal .sls

* ``minion_config``: should include two subkeys..
   - path: the full path to where the minion config should be written
   - contents: the contents of the minion config, as YAML

* ``kickstart_state``: yaml-formatted dictionary to use as the base state to be
  applied. a state should be laid out as follows::
      state_id:
        salt_module:
          - salt_function:
          - arg1: value
          - arg2: value

* ``requirements``: a list of dictionary key: value terms are appended to the
  auto-generated states for git repos, eg the requirements to those states.


The following config is the YAML version of the defaults embedded in
kickstart-oms.py::

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

    # execute these salt modules after kickstart complete
    post_kick:
      - 'state.sls oms.admin'


Kickstart-Kickstart
-------------------

Ensure you have an SSH keypair in ``oms-kickstart/config/keys/``, and capable of
authenticating the git repositories checked out for you during deployment, before
running the kickstart-kickstart scripts.

Run the script, providing the ``user@host`` for SSH and the path to the home
directory of the user on the remote host (no trailing slash):

.. code::

   oms% ./kickstart-kickstart.sh root@162.242.148.144 /root
   ###  Operate on Remote Host: root@162.242.148.144
   ###  $HOME for root@162.242.148.144 is: /root
   The authenticity of host '162.242.148.144 (162.242.148.144)' can't be established.
   ECDSA key fingerprint is 93:e7:27:45:a6:05:9c:ed:0c:25:b0:7c:54:4a:b2:8f.
   Are you sure you want to continue connecting (yes/no)? yes
   Warning: Permanently added '162.242.148.144' (ECDSA) to the list of known hosts.
   root@162.242.148.144's password: 
   ###  ensure local id_rsa.pub is in the remote user's ~/.ssh/authorized_keys
   root@162.242.148.144's password: 
   id_rsa.pub
   
   sent 388 bytes  received 31 bytes  119.71 bytes/sec
   total size is 381  speedup is 0.91
   ###  upload kickstart scripts and configs
   sending incremental file list
   kick-tmux.sh
   kickstart-oms.py
   run-kickstart.sh
   config/
   config/.pillar.yaml.swp
   config/embedded.yaml
   config/example.yaml
   config/latest_dev.yaml
   config/release.yaml
   config/keys/
   config/keys/README
   config/keys/id_rsa
   config/keys/id_rsa.pub
   config/pillar/
   config/pillar/master.yaml
   config/pillar/qa-develop.yaml
   
   sent 16930 bytes  received 271 bytes  11467.33 bytes/sec
   total size is 55267  speedup is 3.21
   ###  upload SSH keys
   sending incremental file list
   id_rsa
   id_rsa.pub
   
   sent 1758 bytes  received 50 bytes  1205.33 bytes/sec
   total size is 2060  speedup is 1.14
   ready to run kickstart! shall we continue? y
   ### in-case there is an open tmux session, try to kill it
   ### this may error out, but that is ok
   failed to connect to server: No such file or directory
   ### starting a new tmux settion, name it kickstart
   ### creating a new window in the session and run kickstart


This will setup everything ``kickstart-oms.py`` needs to run on the remote host,
and will initiate running the script in a tmux session (it basically does what
is described in the previous section about using the kickstart script)..


future intentions
-----------------

* the script currently assumes you want to checkout a git repo to apply the
  states from that repo, but maybe you don't.. so we should support making
  the ``config['repos']['states']`` key as optional (along with all the
  handling of git repositories).
* portability - the script ought to run on any system we want to run OMS on.
