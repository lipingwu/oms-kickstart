OMS Kickstart Dockerfiles
=========================

The files contained in this directory are docker build scripts, known as
Dockerfiles.


Example Use
-----------

Please see http://docs.openmustardseed.org/tutorials/docker_tutorial/ for details
on the setup and use of these Dockerfile.

Each Dockerfile may be used to build an image, just as you would with any other
Dockerfile:

.. code::

   docker build --rm -t=oms/base .
   docker build --rm -t=oms/kick .


Simple.

The `base` image is a stock Ubuntu 12.04 LTS Host plus a few packages, and the
other is that base plug having run oms-kickstart. Be sure to have SSH keys in
``oms-kickstart/config/keys``..


Tips & Tricks
-------------

Docker is a beast in its own right, be sure you learn your way around.

Remove a specific image:

.. code::

   docker rmi oms-kick


Remove all images except the one with `base` in its name:

.. code::

   docker rmi $(docker images | grep -v 'base' | awk {'print $3'})


Remove all containers:

.. code::

   docker rm $(docker ps -a -q)
