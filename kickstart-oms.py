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
Kickstart OMS - To the Cloud!

Expectations:
-------------

 * Only Ubuntu Precise (12.04 LTS) is currently supported
 * User has created an ssh key in /root/.ssh/id_rsa, OR is including one in the
   YAML-formatted config specified as an argument to the script
 * User provides one or more YAML-formatted config files, or uses the defaults
   embedded in this script
 * The intention of this script is to provide a way to easily bootstrap a VM
   with an arbitrary set of salt states, defaulting to those provided in the
   OMS-Kickstart repository on github.


The process:
------------

 * Install Salt Minion Ubuntu Packages (specific version, default is 0.15.3)
 * Overwrite default configs from salt packages. The local minion is configured
   to run in master-less mode - rely only on default grains, do not use pillar
   or top.sls.
 * YAML files are deserialized to get parameters used for next steps.
 * Prepare Salt state HIGH data (dict of states declaration), based on the YAML
   input. Such as is there a SSH private key to install before doing a git
   checkout? Which git repo to checkout? And more.
 * Load salt client that was just installed. It run in local (master-less) mode.
 * Execute all Salt HIGH data, which is checking out all pillars and states Git
   repository in a safe place, where it can execute without interferer with the
   states execution. These are vital to run Salt state.highstate to complete the
   installation of the host.
 * If pillar is not defined in YAML config, use the config itself as pillar data.
 * Synchronize all custom Salt modules, grains, pillars, returners, etc that
   come with the states git previously checkout.
 * run state.highstate.


Other Notes:
------------

 * if no config file(s) are specified, we'll use defaults embedded in this script
 * if config file(s) are specified, they must provide the following config keys
 * this will leave some cruft in /tmp/,  you may wish to delete afterwards


Minimal YAML data:
------------------

repos:
  states:
    oms-kickstart:
      url: git@github.com:IDCubed/oms-kickstart.git
      # specificies the git revision to use, optional
      rev: master
      # specifies the directory within the repo (where to find states) optional
      # copy the whole repo to states path if not set
      copy_path: salt/states

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

kickstart_state:
  # state definition
requirements:
  # list of state requirements associated with states in kickstart_state

pillar:
  # place for arbitrary pillar data - not yet implemented

# if git needs an SSH key, and it isn't in /root/.ssh/ include the private key
ssh_key: |
  -----BEGIN RSA PRIVATE KEY-----
  XXX
  -----END RSA PRIVATE KEY-----

'''
import os
import sys
import pwd
import json
import shutil
import logging
import argparse
import tempfile
import subprocess
from socket import gethostname


# enable and setup logging
logger = logging.getLogger(__name__)

# some defaults for this script
SCRIPT_NAME = 'kickstart-oms.py'

SUPPORTED_DISTROS = [ 'precise', ]

STATES_REPOS = {
    'oms-kickstart': {
        'url': 'git@github.com:IDCubed/oms-kickstart.git',
        'rev': 'master',
        'copy_path': 'salt/states',
    }
}

# saltstate default is /srv/ - return to sane default
INSTALL_DIRECTORY = os.path.join('/' ,'etc', 'salt')
# install states here
STATES_ROOT = os.path.join(INSTALL_DIRECTORY, 'states')
# install pillar here - not implemented
PILLAR_ROOT = os.path.join(INSTALL_DIRECTORY, 'pillar')

# config dictionary for an initial salt-minion
MINION_CONFIG_PATH = os.path.join(INSTALL_DIRECTORY, 'minion')
MINION_CONFIG_CONTENTS = {
    'id': gethostname(),
    'master': '127.0.0.1',
    'log_level': 'debug',
    'file_client': 'local',
    'file_roots': {
        'base': [
            STATES_ROOT
        ],
    },
    'pillar_roots': {
        'base': [
            PILLAR_ROOT
        ],
    },
}

MINION_CONFIG = {
    'path': MINION_CONFIG_PATH,
    'contents': MINION_CONFIG_CONTENTS,
}

BASE_STATES = {
    'base_packages': {
        'pkg':['latest',
              {'names': [
                   'git',
                   'rsync',
                   'openssh-client',
              ]}
        ]
    },
    'ssh_config': {
        'file':['managed',
               {'name': os.path.join('/', 'etc', 'ssh', 'ssh_config')},
               {'contents': os.linesep.join((
                    'Host *',
                    'StrictHostKeyChecking no',
                    'UserKnownHostsFile=/dev/null'))},
               {'require': [
                    {'pkg': 'base_packages'}
                ]}
        ]
    },
    'install_to': {
        'file':['directory',
               {'name': INSTALL_DIRECTORY},
               {'makedirs': True},
        ]
    },
    'salt_minion_files_roots': {
        'file':['directory',
               {'name': STATES_ROOT},
               {'makedirs': True},
               {'clean': True},
               {'require': [
                   {'file': 'install_to'}
               ]}
        ]
    },
    'salt_minion_pillar_roots': {
        'file':['directory',
               {'name': PILLAR_ROOT},
               {'makedirs': True},
               {'clean': True},
               {'require': [
                   {'file': 'install_to'}
               ]}
        ]
    },
}

BASE_REQUIREMENTS = [
    {'pkg': 'base_packages'},
    {'file': 'ssh_config'},
    {'file': 'salt_minion_files_roots'},
    {'file': 'salt_minion_pillar_roots'},
]

# these salt modules/functions are run after everything else
POST_KICK = [
    'state.sls oms.admin',
]

# if creating your own config, this is the bare minimum
DEFAULT_CONFIG = {
        'repos': {
            'states': STATES_REPOS,
        },
        'minion_config': MINION_CONFIG,
        'kickstart_state': BASE_STATES,
        'requirements': BASE_REQUIREMENTS,
        'post_kick': POST_KICK
    }


# running this script will create git repos in /tmp for temporary use, so we
# need to track what we create then remove them.
tmp_paths_to_purge = []


class SSHKey(object):
    '''
    pass for now
    '''
    pass


class GitRepository(object):
    '''
    Represents a local or remote Git repository, and simplifies the work to
    create the highstate data structure salt needs to manage the repository.

    ``id`` and ``url`` are required parameters to denote the name of the repo
    and the url to clone from. ``rev`` specifies the revision to checkout after
    cloning the repo and is optional. lastly, if ``copy_path`` is specified,
    states will guide rsync to copy this path instead of the whole repo.

    '''
    def __init__(self, id, url, rev=None, copy_path=None):
        self.id = id
        self.url = url
        self.rev = rev
        self.copy_path = copy_path

    def __repr__(self):
        if self.rev:
            return '%s (%s)' % (self.url, self.rev)
        return self.url

    def get_states(self,
                   clone_to,
                   requirements,
                   rsync_to=None):
        '''
        compile/return highstate data to clone this git repository, and,
        optionally, have the repo rsync'd to another file path.

        it is expected that ``requirements`` is a list of dictionaries as in::

            {'module': 'state_id'}
            {'pkg': 'base_packges'}

        the highstate data compiled will include:

          ``git.latest`` to be cloned to the path specified by ``clone_to`` and,
          found at ``self.url``.

          a state to remove the .git directory within the repository.

          if defined, add a state to rsync the git repo to the path specified
          by `rsync_to`, If `self.copy_path` specified a path within the cloned
          repo, rsync this instead of the whole repo.

        '''
        output = {
            self.id: {
                'git':['latest',
                      {'name': self.url},
                      {'target': clone_to},
                      {'require': requirements},
                ],
                # do this to prevent a user later from thinking the state parth
                # is a git repo (it's one or more stacked on top of each other)
                'file':['absent',
                       {'name': os.path.join(clone_to, '.git')},
                       {'require': [
                           {'git': self.id}
                       ]}
                ]
            }
        }
        # if we have a specific revision, include it
        if self.rev:
            output[self.id]['git'].append({'rev': self.rev})

        # XXX - part of me thinks we should separate this state into it's own
        # if we are to also rsync this repo somewhere, do so..
        if rsync_to:
            rsync_from = clone_to
            # if a path within the repo was specified, source this rather than
            # the whole repo
            if self.copy_path:
                rsync_from = os.path.join(rsync_from, self.copy_path)
            # the actual rsync command
            rsync_cmd = ('rsync -av %s/ %s/' % (rsync_from, rsync_to))
            # append these details to the state
            output[self.id].update({
                    'cmd':['run',
                          {'name': rsync_cmd},
                          {'require': [
                              {'git': self.id}
                          ]}
                    ]
                }
            )

        return output


def add_logfile_handler(logfile):
    '''
    update logging configuration to write to a file, specified by ``logfile``

    '''
    handler= logging.FileHandler(logfile)
    format = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    handler.setFormatter(format)
    logger.addHandler(handler)


def process_args():
    '''
    process command line arguments passed to the script
    returns parsed args (as a dictionary) from argparse

    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--configs',
                        action='append',
                        nargs='?',
                        default=None,
                        help='one or more YAML-formatted config files')

    parser.add_argument('-d', '--debug',
                        action='store_true',
                        default=False,
                        help='flag to enable/disable debug logging')

    parser.add_argument('-t', '--test',
                        action='store_true',
                        default=False,
                        help='flag to enable/disable test mode, take no action')

    parser.add_argument('-H', '--highstate',
                        action='store_true',
                        default=False,
                        help='run state.highstate to apply states from external repo')

    parser.add_argument('-l', '--logfile',
                        action='store',
                        default=os.path.join('{0}.{1}'.format(SCRIPT_NAME, 'log')),
                        help='specify the file to log to, when in debug mode')

    return parser.parse_args()


def check_state_errors(results):
    '''
    Look for failure within the output of a 'state.high' or 'state.highstate'.
    Expects ``results`` as input but does not return anything, only exits the
    script if an error is found.

    :type results: dict

    '''
    errors = []
    for key in results:
        try:
            if not results[key]['result']:
                try:
                    name = results[key]['name']
                    comment = results[key]['comment']
                except KeyError:
                    errors.append('Invalid output %s' % str(results[key]))
                else:
                    errors.append('State %s failed: %s' % (name, comment))
        except TypeError:
            errors.append('Invalid output %s' % str(results))
    if errors:
        print os.linesep.join(errors)
        sys.exit(1)


def distro_codename():
    '''
    :return: Code name of running distro - eg, 'precise' for Ubuntu 12.04 LTS

    '''
    output = subprocess.check_output(('lsb_release', '-c', '-s'))
    return output.rstrip(os.linesep)


def update_apt(test=False):
    '''
    Run ``apt-get update``. If ``test`` is True, run in noop mode.

    '''
    cmd = ('apt-get', 'update')
    logger.debug(('update apt with: %s' % (cmd,)))
    if not test:
        subprocess.check_call(cmd)


def add_pkg_repository(ppa,
                       test=False):
    '''
    Add a ubuntu ppa. If ``test`` is True, run in noop mode.

    '''
    cmd = ('apt-add-repository', '-y', ppa)
    logger.debug(('Add package repository (%s) with %s' % (ppa, cmd)))
    if not test:
        subprocess.check_call(cmd)


def install_package(package,
                    test=False):
    '''
    install debian pacakge. If ``test`` is True, run in noop mode.

    '''
    cmd = ('apt-get', 'install', '-y', '--force-yes', package)
    logger.debug('Install package %s, running: %s', package, ' '.join(cmd))
    if not test:
        subprocess.check_call(cmd)


def install_salt_minion(stop_service=False,
                        test=False):
    '''
    Install salt-minion from saltstack Ubuntu PPA. If ``stop_service`` is True,
    ensure the salt-minion service is not running after installing the package.

    If ``test`` is True, run in noop mode

    todo:: uncomment stop_service conditional and subprocess.check_call()

    '''
    logger.info('Update apt before we install anything')
    update_apt(test=test)
    logger.info('Install salt-minion package..')
    install_package('python-software-properties', test=test)
    add_pkg_repository('ppa:saltstack/salt', test=test)
    update_apt(test=test)
    install_package('salt-minion', test=test)


def configure_salt_minion(path,
                          config,
                          test=False):
    '''
    Configure salt minion using the provided dictionary ``config``. Note that we
    import yaml python library here because we know that salt-minion package is
    already installed, and py-yaml is a dependency.

    If ``test`` is True, run in noop mode

    '''
    import yaml
    logging.info('Updating config for salt-minion')
    logger.debug(('contents: %s' % json.dumps(config, indent=4)))
    if not test:
        with open(path, 'w') as config_file:
            yaml.dump(config, config_file)


def process_repos(repos=None):
    '''
    create a list of GitRepository classes using the list/dictionary ``repos``

    '''
    gits = []

    for id in repos:
        gits.append(GitRepository(id,
                                  repos[id]['url'],
                                  repos[id].get('rev'),
                                  repos[id].get('copy_path')))
    return gits



def update_kickstart_state(states_repos,
                           base_states={},
                           base_requirements=[],
                           pillar_repos=None,
                           ssh_key=None):
    '''
    Provided a list of ``states repos`` an optional ``pillar_repo``, and an
    optional ``ssh_key``, compile the complete highstate data to kickstart this
    OMS host. ``base_states`` is used as the foundation to add state
    definitions to.

    Note that this is doing one thing that should be made clear: As defined, the
    base states are not correct, we need to update them with the states needed
    for the potential list of repos and SSH key we have received. This list is
    dynamic and states need to be generated/appended to the base states for
    completeness.

    In addition, buried in here is the rsync command we use to copy cloned repos
    to the INSTALL_DIRECTORY.

    :type ssh_key: :class:`SSHKey`

    '''
    states = {}
    states.update(base_states)

    # states - update for git.latest and rsync git repo somewhere else
    # each GitRepo object can render their states, provided some details from us
    for repo in states_repos:
        # create secure tmp directory for our work
        tmp_git = tempfile.mkdtemp()
        # save the path so we can delete it later
        tmp_paths_to_purge.append(tmp_git)
        # update state tree with a few more states for this repo
        states.update(repo.get_states(clone_to=tmp_git,
                                      requirements=base_requirements,
                                      rsync_to=STATES_ROOT))
    # add states for pillar repo(s)
    if pillar_repos:
        for repo in pillar_repos:
            # create secure tmp directory for our work
            tmp_git = tempfile.mkdtemp()
            # save the path so we can delete it later
            tmp_paths_to_purge.append(tmp_git)
            # update state tree with a few more states for this repo
            states.update(repo.get_states(clone_to=tmp_git,
                                          requirements=base_requirements,
                                          rsync_to=PILLAR_ROOT))
    # XXX - not yet supported
    # add states for ssh private key
    if ssh_key is not None:
        states.update(ssh_key.get_states())
        requirements.append(ssh_key.require)

    return states


def get_salt_client():
    '''
    helper function to import ``salt.client`` and return
    ``salt.client.Caller().function``

    '''
    # XXX - this module_dir bit is not portable, what to do about it?
    module_dir = '/usr/lib/pymodules/python%d.%d' % (sys.version_info.major,
                                                     sys.version_info.minor)
    if module_dir not in sys.path:
        sys.path.append(module_dir)
    # import and return salt client as if we called salt-call. note that this
    # expects the minion config has file_client: local
    import salt.client
    return salt.client.Caller().function


def load_yaml_configs(file_list):
     '''
     Create a dict of data from multiple YAML files.

     Note that files are loaded in the order recieved, it is your responsibility
     to ensure these files don't step on each other.

     '''
     import yaml
     output = {}
     for config in file_list:
         try:
             with open(config) as yaml_file:
                 try:
                     data = yaml.safe_load(yaml_file)
                     output.update(data)
                     logger.debug(('contents of YAML config %s: %s' % (config, data)))
                 except Exception, err:
                     logger.error('Unable to parse contents of YAML file %s: %s',
                                  config, err)
         except IOError:
             logger.error('Unable to open %s', config)
     return output


def main():
    '''
    let the real work begin!

    '''
    args = process_args()

    # set log level and setup logging
    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG

    logging.basicConfig(level=log_level,
                        stream=sys.stderr,
                        format='%(asctime)s [%(process)d] %(message)s')
    # write to a logfile, when in debug mode
    if args.debug:
        add_logfile_handler(args.logfile)

    logger.debug(('Script args: %s' % args))

    if args.test:
        logging.info('Test mode enabled, no actions will be taken')

    # check distribution, error out if not supported
    distro = distro_codename()
    logger.debug(('OS Distro: %s' % distro))
    if distro not in SUPPORTED_DISTROS:
        print '%s does not support %s' % (SCRIPT_NAME, distro)
        sys.exit(1)

    install_salt_minion(test=args.test)
    # as YAML can only be assumed to be importable after Salt minion is
    # installed (PyYAML is a salt dependency), we load YAML configs after
    config = DEFAULT_CONFIG
    if args.configs:
        config = load_yaml_configs(args.configs)
        logger.debug(('imported YAML configs from: %s' % args.configs))
        logger.debug(('config:\n%s' % json.dumps(config, indent=4)))

    configure_salt_minion(config['minion_config']['path'],
                          config['minion_config']['contents'],
                          test=args.test)

    try:
        states_repos_list = config['repos']['states']
        logger.debug(('state repos: %s' % states_repos_list))
    except KeyError:
        print 'Missing config key repos:states in %s' % config
        sys.exit(1)

    states_repos = process_repos(states_repos_list)

    try:
        pillar_repos = process_repos(config['repos']['pillar'])
    except KeyError:
        logger.info('no pillar repo found in config, skipping')
        pillar_repos = None

    try:
        ssh_key = SSHKey(config['ssh_key'])
    except KeyError:
        logger.info('Missing SSH key configuration, hope Git repo is public.')
        ssh_key = None

    data = update_kickstart_state(states_repos,
                                  config['kickstart_state'],
                                  config['requirements'],
                                  pillar_repos,
                                  ssh_key)
    if args.debug:
        import yaml
        logger.debug(('updated kickstart state (yaml):\n%s' % yaml.dump(data,
                                                                        indent=4)))

    if not args.test:
        logger.debug('loading salt client')
        salt_client = get_salt_client()

        logger.debug('running state.high to apply base states')
        check_state_errors(salt_client('state.high', data))
        # we've applied the base states, sync modules/states so minion is current
        salt_client('saltutil.sync_all')
        # run state.highstate, if the user has told us to. if the base states
        # setup the host with more states, or a top.sls, this will effectively
        # apply those updates
        if args.highstate:
            logger.debug('run state.highstate to apply states from external repo')
            salt_client('state.highstate')
        # we're done with kickstart core, so run extra modules if specified
        if config.has_key('post_kick'):
            for run_me in config['post_kick']:
                logger.debug('calling post kickstart function %s' % run_me)
                # rework input: salt_client(func, [arg1, arg2])
                f = run_me.split(' ')
                func = [f[0], f[1:]]
                salt_client(*func)
        # remove all the temporary git repos we cloned.. but skip if in debug mode
        if not args.debug:
            for repo in tmp_paths_to_purge:
                logger.info(('remove temporary path: %s' % repo))
                shutil.rmtree(repo)
    else:
        logger.info('in test mode.. skipping state execution')


if __name__ == '__main__':
    main()
