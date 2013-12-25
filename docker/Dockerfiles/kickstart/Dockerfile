FROM oms/base:latest

MAINTAINER info@idcubed.org

# run-kickstart.sh expects to have $HOME set
ENV HOME /root

# ensure the container has the SSH pubkey setup it needs
RUN mkdir /root/.ssh
ADD oms-kickstart/config/keys/id_rsa /root/.ssh/
ADD oms-kickstart/config/keys/id_rsa.pub /root/.ssh/
# right now, the salt states expect authorized_keys to exist, create it!
RUN touch /root/.ssh/authorized_keys
# tighten up permissions
RUN chmod -R o-wrx /root/.ssh
RUN chmod -R g-wrx /root/.ssh

# setup kickstart scripts and config
# begin ignition sequence!
RUN mkdir /root/kickstart
ADD oms-kickstart/config /root/kickstart/config
ADD oms-kickstart/kickstart-oms.py /root/kickstart/
ADD oms-kickstart/run-kickstart.sh /root/kickstart/

# ba-BOOM!
RUN /bin/bash -c /root/kickstart/run-kickstart.sh 
