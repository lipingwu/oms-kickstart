-------------
OMS-Kickstart
-------------

Kickstart a User to The Cloud!


the script..
------------

 * updates apt
 * installs git
 * runs salt's kickstart script
 * sprinkles some salt (config, states, pillar) into /etc/salt/
 * and runs salt-call --local state.sls kick.start (where kick.start is a salt state file /etc/salt/states/kick/start.sls


caveats
-------

 * requires Ubuntu 12.04 LTS until otherwise noted
 * completely brand new and under development - you have been warned!
