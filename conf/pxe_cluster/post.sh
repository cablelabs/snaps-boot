#!/usr/bin/env bash
cat > /etc/apt/sources.list <<EOF
deb http://archive.ubuntu.com/ubuntu/ xenial main restricted
deb http://archive.ubuntu.com/ubuntu/ xenial-updates main restricted
deb http://archive.ubuntu.com/ubuntu/ xenial universe
deb http://archive.ubuntu.com/ubuntu/ xenial-updates universe
deb http://archive.ubuntu.com/ubuntu/ xenial multiverse
deb http://archive.ubuntu.com/ubuntu/ xenial-updates multiverse
deb http://archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu xenial-security main restricted
deb http://security.ubuntu.com/ubuntu xenial-security universe
deb http://security.ubuntu.com/ubuntu xenial-security multiverse
EOF




apt-get -f -y install
apt-get -qq -y autoremove
apt-get clean
apt-get -qq -y update
apt-get -qq -y install python
apt-get -qq -y install cloud-init
apt-get -qq -y install libltdl7
sed -i 's/prohibit-password/yes/' /etc/ssh/sshd_config
service ssh restart

apt-get -y install ntp
cat >> /etc/ntp.conf <<EOF
server 172.16.141.17 iburst
EOF


#Get the MAC for the first working NIC
ADMIN_MAC=$(ip a | grep -v lo| awk 'f{print $2;f=0;exit} /UP/{f=1}')
CLOUD_INIT_IP=10.197.143.11
sed -E -i "s/GRUB_CMDLINE_LINUX=\"\"/GRUB_CMDLINE_LINUX=\" console=ttyS1,115200  ds=nocloud-net cloud-config-url=http:\/\/$CLOUD_INIT_IP\/latest\/meta-data\/$ADMIN_MAC \"/g" /etc/default/grub
update-grub
cat >> /etc/modprobe.d/nest.conf <<EOF
options kvm_intel nested=1
EOF