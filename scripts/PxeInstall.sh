#!/bin/bash
cr=`echo $'\n.'`
cr=${cr%.}

# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG SARL and Cable Television Laboratories, Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

####################################################################################
#Script name : PxeInstall.sh                                                       #
#Author      : Yashwant Bhandari                                                   #
#Date        : 21/04/2017                                                          #
#Platform    : Ubuntu 16.04                                                        #
#Purpose     : Used to perform following operations-                               #
#               -set http,https,ftp proxy                                          #
#               -install , configure , restart  isc-dhcp-server                    #
#               -install ,configure  ,restart apache2 tftpd-hpa inetutils-inetd    #
#               -mount ubuntu iso                                                  #
####################################################################################


echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "PxeInstallation Script"
echo "++++++++++++++++++++++++++++++++++++++++++++++"

checkStatus () {
#echo "checkStatus method for $2 "
command_status=$1
if [ $command_status != "0" ]
then
echo " last command $2 not executed successfully :: exit the script"
exit 0
else
echo " last command $2 executed successfully "
fi
}


setProxy () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "setProxy method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
export http_proxy=$1
export https_proxy=$1
export ftp_proxy=$1
export -p
}





dhcpInstall () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "dhcpInstall method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
pxeServerPass="$2"
echo "$pxeServerPass"  | sudo -S apt-get -y install isc-dhcp-server
command_status=$?
checkStatus $command_status "install dhcp-server using apt-get"
#sudo apt-get --purge remove isc-dhcp-server
sleep 5
}







dhcpRestart () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "dhcpRestart  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
pxeServerPass="$1"
echo "$pxeServerPass" | sudo -S systemctl stop isc-dhcp-server
echo "$pxeServerPass" | sudo -S systemctl start isc-dhcp-server
}


tftpAndApacheInstall () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "tftpAndApacheInstall  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
pxeServerPass="$1"
echo "$pxeServerPass" | sudo -S   apt-get -y install apache2 tftpd-hpa
#inetutils-inetd
command_status=$?
checkStatus $command_status "install tftp server  And Apache server  using apt-get"
#sudo apt-get --purge remove apache2 tftpd-hpa inetutils-inetd

}


tftpConfigure () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "tftpConfigure  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
pxeServerPass="$2"
temp_dir="$PWD"/conf/pxe_cluster

echo "tftpConfigure :: save backup  of file /etc/default/tftpd-hpa "
echo "$pxeServerPass" | sudo -S cp /etc/default/tftpd-hpa /etc/default/tftpd-hpa.bkp
command_status=$?
checkStatus $command_status "backup of /etc/default/tftpd-hpa"

if [ "$1" = "tftpdHpa" ]
then
cat <<EOF >$temp_dir/tftpd-hpa
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/var/lib/tftpboot"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="--secure"
RUN_DAEMON="yes"
OPTIONS="-l -s /var/lib/tftpboot"
EOF
command_status=$?
checkStatus $command_status " creation of tftpd-hpa local"

#copy this local data  to the original file location

cp $temp_dir/tftpd-hpa  /etc/default/tftpd-hpa
command_status=$?
checkStatus $command_status " writing data of local tftpd-hpa  to  /etc/default/tftpd-hpa"


elif [ $1 = "inetdConf" ]
then
cat <<EOF >$temp_dir/inetd.conf
tftp    dgram   udp    wait    root    /usr/sbin/in.tftpd /usr/sbin/in.tftpd -s /var/lib/tftpboot
EOF
command_status=$?
checkStatus $command_status " creation of inetd.conf local "

#copy this local file  data  to the original file

cp $temp_dir/inetd.conf  /etc/inetd.conf
command_status=$?
checkStatus $command_status " writing data of local inetd.conf  to  /etc/inetd.conf"
else
  echo "Both strings are different"
fi

}



tftpdHpaRestart () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "tftpdHpaRestart method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
pxeServerPass="$1"
echo "$pxeServerPass" | sudo -S systemctl stop tftpd-hpa
echo "$pxeServerPass" | sudo -S systemctl start tftpd-hpa
command_status=$?
checkStatus $command_status " tftpdHpaRestart "

}



mountAndCopy () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "mountAndCopy  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
pxeServerPass="$2"
if [ -f packages/images/"$1" ] #if [ "$1" ] #
then
    echo "ISO file $1 exists."
	echo "$pxeServerPass" | sudo -S  mount -o  loop packages/images/$1 /mnt

	sleep 10
	echo "$pxeServerPass" | sudo -S mkdir /var/www/html/ubuntu
	echo "$pxeServerPass" | sudo -S cp -fr /mnt/* /var/www/html/ubuntu/

else
    echo "Error: ISO file $1  does not exists."
	exit 0
fi
sleep 10

if [ -d "/var/lib/tftpboot/" ]
	then
	echo "Directory tftpboot exists. "
	# un comment below lines
	echo "$pxeServerPass" | sudo -S  cp -fr /var/www/html/ubuntu/install/netboot/* /var/lib/tftpboot/
	command_status=$?
	checkStatus $command_status " copy files from  /var/www/html/ubuntu/install/netboot/* to /var/lib/tftpboot/  "
   fi

}

mountAndCopyUefi () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "mountAndCopy  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
pxeServerPass="$3"
if [ -f packages/images/"$1" ] #if [ "$1" ] #
then
    echo "Grub file $1 exists."
	echo "$pxeServerPass" | sudo -S  cp -fr packages/images/$1 /var/lib/tftpboot
else
    echo "Error: Grub file $1  does not exists."
	exit 0
fi
}


defaultFileConfigure () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "defaultFileConfigure  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
temp_dir="$PWD"/conf/pxe_cluster
pxeServerPass="$3"

echo "defaultFileConfigure :: save backup  of file /var/lib/tftpboot/pxelinux.cfg/default "
echo "$pxeServerPass" | sudo -S cp /var/lib/tftpboot/pxelinux.cfg/default /var/lib/tftpboot/pxelinux.cfg/default.bkp
command_status=$?
checkStatus $command_status "backup of /var/lib/tftpboot/pxelinux.cfg/default  file"

echo "defaultFileConfigure ::  create  local file default"
#echo "$1 is the pxeServerIp ip here
#echo "$2 is the used seedFile name here

cat <<EOF >$temp_dir/default
default menu.c32
prompt
timeout 100
ONTIMEOUT ubuntu

menu hshift 13
menu width 70
menu margin 8
menu tabmsg

menu title ####### Automated PXE Boot Menu #######

label ubuntu
menu label ^1) Install Ubuntu
path ubuntu-installer/amd64/boot-screens/
include ubuntu-installer/amd64/boot-screens/menu.cfg
default ubuntu-installer/amd64/boot-screens/vesamenu.c32
prompt 0
timeout 100

label centos
menu label ^2) Install CentOS
kernel centos7/vmlinuz
append initrd=centos7/initrd.img ks=http://$1:/centos7/ks.cfg

label local_drive
menu label ^3) Boot from local drive
localboot 0
EOF
command_status=$?
checkStatus $command_status " creation of default file "


#copy this local data  to the original file
cp $temp_dir/default  /var/lib/tftpboot/pxelinux.cfg/
command_status=$?
checkStatus $command_status " writing data of local default  to  /var/lib/tftpboot/pxelinux.cfg/default"

}



defaultGrubConfigure () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "defaultGrubConfigure  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
temp_dir="$PWD"/conf/pxe_cluster
pxeServerPass="$5"

if [ ! -d "/var/lib/tftpboot/grub" ]
	then
	echo "Creating Grub Config Directory "
	# un comment below lines
	echo "$pxeServerPass" | sudo -S  mkdir  /var/lib/tftpboot/grub
	command_status=$?
	checkStatus $command_status " making directory /var/lib/tftpboot/grub  "
   fi


if [ -f "/var/lib/tftpboot/grub/grub.cfg" ]
	then
    echo "defaultGrubConfigure :: save backup  of file /var/lib/tftpboot/ "
    echo "$pxeServerPass" | sudo -S cp /var/lib/tftpboot/grub/grub.cfg /var/lib/tftpboot/grub.bkp
    command_status=$?
    checkStatus $command_status "backup of /var/lib/tftpboot/grub/grub.cfg  file"
   fi



echo "defaultGrubConfigure ::  create  local file grub.cfg"
#echo "$1 is the pxeServerIp ip here
#echo "$2 is the used seedFile name here
#echo "$3 is the hostname
#echo "$4 is the interface

cat <<EOF >$temp_dir/grub.cfg
set default 0
set timeout=10

menuentry "Install Ubuntu 16" {
set gfxpayload=keep
linux ubuntu-installer/amd64/linux gfxpayload=800x600x16,800x600 netcfg/choose_interface=$4 live-installer/net-image=http://$1/ubuntu/install/filesystem.squashfs --- auto=true url=http://$1/ubuntu/preseed/$2 ks=http://$1/ubuntu/ks.cfg
initrd ubuntu-installer/amd64/initrd.gz
}
EOF
command_status=$?
checkStatus $command_status " creation of grub file "

#copy this local data  to the original file
cp $temp_dir/grub.cfg  /var/lib/tftpboot/grub/grub.cfg
command_status=$?
checkStatus $command_status " writing data of local grub  to  /var/lib/tftpboot/grub/grub.cfg"
}

bootMenuConfigure () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "bootMenuConfigure  method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
temp_dir="$PWD"/conf/pxe_cluster
pxeServerPass="$3"

echo "bootMenuConfigure :: save backup  of file /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/menu.cfg "
echo "$pxeServerPass" | sudo -S cp /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/menu.cfg /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/menu.cfg.bkp
command_status=$?
checkStatus $command_status "backup of /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/menu.cfg  file"

echo "bootMenuConfigure ::  create  local file default"

cat <<EOF >$temp_dir/menu.cfg
menu hshift 13
menu width 49
menu margin 8
menu title installer boot menu
        kernel ubuntu-installer/amd64/linux
        append ks=http://$1/ubuntu/ks.cfg vga=normal initrd=ubuntu-installer/amd64/initrd.gz  url=http://$1/ubuntu/preseed/$2 live-installer/net-image=http://$1/ubuntu/install/filesystem.squashfs console=ttyS1,115200 console=ttyS0,115200 console=tty ramdisk_size=16432 root=/dev/rd/0 rw  --

EOF
command_status=$?
checkStatus $command_status " creation of menu.cfg file "


#copy this local data  to the original file
cp $temp_dir/menu.cfg  /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/
command_status=$?
checkStatus $command_status " writing data of local menu.cfg  to  /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/menu.cfg"

}

defaultFileConfigureUbuntu () {
echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "defaultFileConfigureUbuntu method "
echo "++++++++++++++++++++++++++++++++++++++++++++++"
temp_dir="$PWD"/conf/pxe_cluster
pxeServerPass="$3"

echo "defaultFileConfigureUbuntu :: save backup  of file /var/lib/tftpboot/pxelinux.cfg/default "
echo "$pxeServerPass" | sudo -S cp /var/lib/tftpboot/pxelinux.cfg/default /var/lib/tftpboot/pxelinux.cfg/default.bkp
command_status=$?
checkStatus $command_status "backup of /var/lib/tftpboot/pxelinux.cfg/default  file"

echo "defaultFileConfigureUbuntu ::  create  local file default"
#echo "$1 is the pxeServerIp ip here
#echo "$2 is the used seedFile name here

cat <<EOF >$temp_dir/default
default menu.c32
prompt
timeout 100
ONTIMEOUT ubuntu

menu hshift 13
menu width 70
menu margin 8
menu tabmsg

menu title ####### Automated PXE Boot Menu #######

label ubuntu
menu label ^1) Install Ubuntu
path ubuntu-installer/amd64/boot-screens/
include ubuntu-installer/amd64/boot-screens/menu.cfg
default ubuntu-installer/amd64/boot-screens/vesamenu.c32
prompt 0
timeout 100

label local_drive
menu label ^2) Boot from local drive
localboot 0
EOF
command_status=$?
checkStatus $command_status " creation of default file "

#copy this local data  to the original file
cp $temp_dir/default  /var/lib/tftpboot/pxelinux.cfg/
command_status=$?
checkStatus $command_status " writing data of local default  to  /var/lib/tftpboot/pxelinux.cfg/default"

}


#main function execution


case "$1" in
   "installPreReq")
      echo "++++++++++++++++++apt-get update++++++++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S apt-get -y update
      echo " "
      echo "++++++++++++++++++apt-get install python++++++++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S apt-get install -y python
      echo " "
      echo "$2" | sudo -S apt-get install -y python-pathlib
      echo " "
      echo "$2" | sudo -S apt-get install -y python-yaml
      echo " "
      echo "$2" | sudo -S apt-get install -y python-six
      echo "++++++++++++++++++apt-get install openssh-server++++++++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S apt-get install -y openssh-server
      echo " "
      echo "+++++++++++++++++++++++apt-get install ansible+++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S sudo apt-get install -y ansible
      echo " "
      echo "+++++++++++++++++++++++apt-get install ntp+++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S sudo apt-get install -y ntp
      echo " "
      echo "++++++++++++++++++++++++++++++++++++++++++++++"
      echo "++++++++++++++++++pip installs++++++++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S pip install --upgrade pip
      echo "$2" | sudo -S pip install ansible
      echo " "
      echo "++++++++++++++++++++++++++++++++++++++++++++++"
      echo "++++++++++++++++++apt-get install dos2unix++++++++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S apt-get install -y dos2unix
      echo " "
      echo "+++++++++++++++++++++++apt-get install ipmitool+++++++++++++++++++++++"
      echo " "
      echo "$2" | sudo -S apt-get install -y ipmitool
      echo "++++++++++++++++++++++++++++++++++++++++++++++"
      sleep 10
       ;;

      setGlobalValues)
       echo " "
        ;;

	setProxy)

	setProxy "$2"
	;;


 	dhcpInstall)
	dhcpInstall "$2" "$3"
	;;


 	dhcpConfigure)
      	#echo "$2"
	#test
	argumentsFrom2=""
	count=0
	for argument in $*
	do
	count=`expr $count + 1`
	if [ $count  -lt 2 ]  # this is the condition to control the number of arguments
	then
	echo " "
	else
	argumentsFrom2=$argumentsFrom2" "$argument
	fi
	done
	dhcpConfigure $argumentsFrom2

	#dhcpConfigure "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "$10"
	 ;;
 	# $3 is the name of interface card

 	dhcpRestart)
      	dhcpRestart "$2"
	;;

	tftpAndApacheInstall)
      	tftpAndApacheInstall "$2"
	;;

	tftpConfigure)
      	tftpConfigure "$2" "$3"
	;;

	tftpdHpaRestart)
      	tftpdHpaRestart "$2"
	 ;;


	mountAndCopy)
      	mountAndCopy "$2"  "$3"
	;;

	mountAndCopyUefi)
      	mountAndCopyUefi "$2"  "$3" "$4"
	;;

	defaultFileConfigure)
      	defaultFileConfigure "$2" "$3" "$4"
	 ;;

	defaultFileConfigureUbuntu)
      	defaultFileConfigureUbuntu "$2" "$3" "$4"
	 ;;

        bootMenuConfigure)
        bootMenuConfigure "$2" "$3" "$4"
         ;;

	defaultGrubConfigure)
      	defaultGrubConfigure "$2" "$3" "$4" "$5" "$6"
	 ;;


esac
