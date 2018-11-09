#!/bin/sh
# Some notes from installing VirtualBox on CentOS 7. 
# based on: https://gist.github.com/paulmaunders/3e2cbe02c07b6393f7ef0781eed9f97b
# Install dependencies
yum -y install gcc make patch  dkms qt libgomp
yum -y install kernel-headers kernel-devel fontforge binutils glibc-headers glibc-devel
yum -y install "kernel-devel-uname-r == $(uname -r)"

# Install VirtualBox
cd /etc/yum.repos.d
wget http://download.virtualbox.org/virtualbox/rpm/rhel/virtualbox.repo
yum -y install VirtualBox-5.2

# Build the VirtualBox kernel module 
export KERN_DIR=/usr/src/kernels/$(uname -r)
export KERN_VER=$(uname -r)
/sbin/rcvboxdrv setup

# Install Vagrant
yum -y install https://releases.hashicorp.com/vagrant/2.1.1/vagrant_2.1.1_x86_64.rpm
