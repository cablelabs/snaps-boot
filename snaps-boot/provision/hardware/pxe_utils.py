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

"""
Purpose : PxeServer Provisioning
Date :21/04/2017
Created By :Yashwant Bhandari
"""
import fileinput
import subprocess
import os
from os import remove, close
import sys
from common.utils import file_utils
from tempfile import mkstemp
import re
import logging
import shutil
from shutil import move
from common.consts import consts
from ansible_p.ansible_utils import ansible_playbook_launcher
import os.path
logger = logging.getLogger('deploy_venv')
def __main(config,operation):
 provDict=config.get('PROVISION')
 dhcpDict=provDict.get('DHCP')
 proxyDict=provDict.get('PROXY')
 pxeDict=provDict.get('PXE')
 tftpDict=provDict.get('TFTP')
 staticDict=provDict.get('STATIC')
 bmcDict=provDict.get('BMC')
 subnet_list=dhcpDict.get('subnet')
 cpuCoreDict=provDict.get('CPUCORE')

 if operation == "hardware":
  #print "hardware option"
  __pxe_server_installation(provDict,dhcpDict,proxyDict,pxeDict,tftpDict,staticDict,subnet_list)
 elif operation == "boot":
  __pxeBoot(bmcDict)
 elif operation == "bootd":
  __pxeBootd(bmcDict)
 elif operation == "provisionClean":
  __provisionClean()
 elif operation == "staticIPConfigure":
  print 'AAAAA'
  __staticIPConfigure(staticDict,tftpDict,proxyDict)
 elif operation == "staticIPCleanup":
  print 'AAAAA'
  __staticIPCleanup(staticDict,tftpDict)
 elif operation == "setIsolCpus":
  __setIsolCpus(tftpDict,cpuCoreDict)
 elif operation == "delIsolCpus":
  __delIsolCpus(tftpDict,cpuCoreDict)
  #__addDhcpdFile(provDict,dhcpDict,subnet_list)
  #__moveDhcpdFile()
  #__addIscDhcpFile(pxeDict,subnet_list)
 else:
  print "Cannot read configuration"






def __pxe_server_installation(provDict,dhcpDict,proxyDict,pxeDict,tftpDict,staticDict,subnet_list):
    """
     This will launch the shell script to  install and configure dhcp , tftp and apache server.

     :param config:the config data in form of dictionary from hosts.yaml
     :return:
    """
    logger.info("pxe_server_installation")
    logger.info("***********************set proxy**********************")
    os.system('sh scripts/PxeInstall.sh setProxy '+proxyDict["http_proxy"] )
    logger.info("****************installPreReq ************************")
    os.system('sh scripts/PxeInstall.sh installPreReq '+pxeDict["password"] )
    logger.info("****************dhcpInstall***************************")
    os.system('sh scripts/PxeInstall.sh dhcpInstall '+proxyDict["http_proxy"]+" "+pxeDict["password"] )
    logger.info("*******dhcpConfigure iscDhcpServer*********************")
    __addIscDhcpFile(pxeDict,subnet_list)
    logger.info("*******dhcpConfigure generate  dhcpd.conf file***********")
    __addDhcpdFile(provDict,dhcpDict,subnet_list)
    __moveDhcpdFile()
    logger.info("****************dhcpRestart****************************")
    __dhcpRestart()

    logger.info("****************ftpAndApacheInstall********************")
    os.system('sh scripts/PxeInstall.sh tftpAndApacheInstall '+proxyDict["http_proxy"]+" "+pxeDict["password"] )
    logger.info("**********tftpConfigure tftpdHpa***********************")
    os.system('sh scripts/PxeInstall.sh tftpConfigure tftpdHpa'+" "+pxeDict["password"])
    #logger.info("**************tftpConfigure inetdConf******************")
    #os.system('sh scripts/PxeInstall.sh tftpConfigure inetdConf'+" "+pxeDict["password"])
    logger.info("******************tftpdHpaRestart**********************")
    os.system('sh scripts/PxeInstall.sh tftpdHpaRestart'+" "+pxeDict["password"])
    logger.info("******************mountAndCopy************************")
    os.system('sh scripts/PxeInstall.sh mountAndCopy '+tftpDict["os"]+" "+pxeDict["password"] )
    logger.info("*************defaultFileConfigure********************")
    os.system('sh scripts/PxeInstall.sh defaultFileConfigure '+pxeDict["serverIp"]+" "+tftpDict["seed"]+" "+pxeDict["password"] )
    logger.info("*************bootMenuConfigure********************")
    os.system('sh scripts/PxeInstall.sh bootMenuConfigure '+pxeDict["serverIp"]+" "+tftpDict["seed"]+" "+pxeDict["password"] )
    logger.info("*********validateAndCreateconfigKsCfg****************")
    __validateAndCreateconfigKsCfg(pxeDict,tftpDict,proxyDict)
    logger.info("****************configureAnsibleFile*****************")
    __configureAnsibleFile()
    __configureNTPServerFile(pxeDict)
    __restartNTPServer(pxeDict)

def __validateAndCreateconfigKsCfg(pxeDict,tftpDict,proxyDict):
 """
 used to configure ks.cfg file
 :param config : pxeDict , tftpDict ,proxyDict (dictionary data from hosts.yaml file)
 :return
 """
 os.system('dos2unix conf/pxe_cluster/ks.cfg')
 logger.info("configuring   timezone in ks.cfg")
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"timezone","timezone  "+tftpDict["timezone"])

 print " "
 logger.debug("configuring   client user password   name in ks.cfg")
 user_cridentials="user "+tftpDict["user"]+" --fullname "+tftpDict["fullname"]+" --password "+tftpDict["password"]
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"user",user_cridentials)

 print " "
 logger.debug("configuring   client root password   name in ks.cfg")
 user_cridentials="rootpw "+tftpDict["password"]
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"rootpw",user_cridentials)

 print" "
 logger.debug("configuring server url  in ks.cfg")
 my_url="url --url http://"+pxeDict["serverIp"]+"/ubuntu/"
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"url",my_url)

 print" "
 logger.debug("configuring ntp server ip  in ks.cfg")
 ntp_server="server "+pxeDict["serverIp"]+" iburst"
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"server",ntp_server)

 print" "
 logger.debug("configuring http proxy  in ks.cfg")
 httpProxy="Acquire::http::Proxy "+"\""+ proxyDict["http_proxy"]+"\";"
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"Acquire::http::Proxy",httpProxy)

 print" "
 logger.debug("configuring https proxy  in ks.cfg")
 httpsProxy="Acquire::https::Proxy "+"\""+proxyDict["https_proxy"]+"\";"
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"Acquire::https::Proxy",httpsProxy)

 print" "
 logger.debug("configuring ftp proxy  in ks.cfg")
 ftpProxy="Acquire::ftp::Proxy "+"\"" + proxyDict["ftp_proxy"]+"\";"
 __searchAndReplace('conf/pxe_cluster/ks.cfg',"Acquire::ftp::Proxy",ftpProxy)

 print" "
 logger.debug("copy local ks.cfg to location /var/www/html/ubuntu/")
 os.system('cp conf/pxe_cluster/ks.cfg /var/www/html/ubuntu/')

def __searchAndReplace(fname, pat, s_after):
  """
  search a line start with pat in file fname  and replace that whole line by string s_after
  :param config : pat string to search a line start with , s_after string to replace the line
  :return
  """
  # first, see if the pattern is even in the file.
  # if line start with pat, then replace  whole line by subst
  #os.system('dos2unix '+fname)
  with open(fname) as f:
    out_fname = fname + ".tmp"
    out = open(out_fname, "w")
    #logger.debug("changing pattern "+pat +" --> "+s_after )
    for line in f:
       if re.match(pat,line):
        logger.info("changing pattern "+pat +" --> "+s_after )
        line = s_after +"\n"
       out.write(line)
    out.close()
    os.rename(out_fname, fname)



def __configureAnsibleFile():
 """
 to uncomment host_key_checking field in ansible.cfg file
 :param config
 :return
 """
 print" "
 logger.info("configureAnsibleFile function")
 file_path="/etc/ansible/ansible.cfg"
 os.system('dos2unix '+file_path)
 if os.path.exists(file_path):
  logger.info(file_path+" file exists")
  #__searchAndReplace(file_path,"#inventory","inventory      = /etc/ansible/hosts")
  __searchAndReplace(file_path,"#host_key_checking","host_key_checking = False")



def __configureNTPServerFile(pxeDict):
 """
 to  configure   ntp.conf file
 :param config : pxeDict
 :return
 """
 print" "
 logger.info("configureNTPServerFile function")
 file_path="/etc/ntp.conf"
 os.system('dos2unix '+file_path)
 if os.path.exists(file_path):
  logger.info(file_path+" file exists")
  os.system('echo '+pxeDict["password"] +  ' | sudo -S cp /etc/ntp.conf /etc/ntp.conf_bkp')
  __searchAndReplace(file_path,"pool 0.ubuntu.pool.ntp.org iburst","#pool 0.ubuntu.pool.ntp.org iburst")
  __searchAndReplace(file_path,"pool 1.ubuntu.pool.ntp.org iburst","#pool 1.ubuntu.pool.ntp.org iburst")
  __searchAndReplace(file_path,"pool 2.ubuntu.pool.ntp.org iburst","#pool 2.ubuntu.pool.ntp.org iburst")
  __searchAndReplace(file_path,"pool 3.ubuntu.pool.ntp.org iburst","#pool 3.ubuntu.pool.ntp.org iburst")
  __searchAndReplace(file_path,"pool ntp.ubuntu.com","#pool ntp.ubuntu.com")
  __searchAndReplace(file_path,"#server 127.127.22.1","server 127.127.1.0 prefer")



def __restartNTPServer(pxeDict):
 """
 to  restart ntp server
 :param config : pxeDict
 :return
 """
 print" "
 logger.info("restartNTPServer function")
 os.system('echo '+pxeDict["password"] +' |  sudo -S systemctl restart  ntp.service')
 os.system('echo '+pxeDict["password"] +' |  sudo -S systemctl status  ntp.service')



def __addDhcpdFile(provDict,dhcpDict,subnet_list):
 """
 to  generate  local dhcpd.conf file
 :param config :
 :return
 """
 print" "
 logger.info("addDhcpdFile function")
 common_str="""
 ddns-update-style none;
 default-lease-time 1600;
 max-lease-time 7200;
 authoritative;
 log-facility local7;
 allow booting;
 allow bootp;
 option option-128 code 128 = string;
 option option-129 code 129 = text;
 #next-server X.X.X.X;
 filename "pxelinux.0";  """

 file_path="conf/pxe_cluster/dhcpd.conf"
 os.system('dos2unix '+file_path)
 if os.path.exists(file_path):
  logger.info(file_path+" file exists")
  os.system('cp conf/pxe_cluster/dhcpd.conf conf/pxe_cluster/dhcpd.conf.bkp')
 config_dict = {}
 with open(file_path, "w") as text_file:
 	text_file.write(common_str)
	text_file.write("\n")
	for subnet in subnet_list:
		name = subnet.get('name')
		type = subnet.get('type')
		address = subnet.get('address')
		range = subnet.get('range')
		netmask = subnet.get('netmask')
		router = subnet.get('router')
		broadcast = subnet.get('broadcast-address')
		default_lease = subnet.get('default-lease')
		max_lease = subnet.get('max-lease')
		listen_iface = subnet.get('listen_iface')
		dns = subnet.get('dns')
		dn = subnet.get('dn')
		subnet_d= "subnet "+ address + " netmask " + netmask + "{" + "\n" + "  range " + range + ";" + "\n" + "  option domain-name-servers " + dns + ";" + "\n" + "  option domain-name \"" + dn + "\";" + "\n" + "  option subnet-mask " + netmask + ";" + "\n" + "  option routers " + router + ";" + "\n" + "  option broadcast-address "+broadcast + ";" + "\n" + "  default-lease-time " + str(default_lease) + ";" + "\n" + "  max-lease-time " + str(max_lease) + ";" + "\n" + "  deny unknown-clients;" + "\n" + "}"
		text_file.write(subnet_d)
		text_file.write("\n")

		mac_ip_list=subnet.get('bind_host')
		for mac_ip in mac_ip_list:
			host_sub= "host ubuntu-client-"+ mac_ip.get('ip')+" {" +"\n" + "  hardware ethernet " + mac_ip.get('mac')+ ";" + "\n" + "  fixed-address " + mac_ip.get('ip')+";" + "\n" + "}"
			text_file.write(host_sub)
			text_file.write("\n")






def __moveDhcpdFile():
 """
 to  move local dhcpd  file
 :param config :
 :return
 """
 print" "
 logger.info("moveDhcpdFile function")
 file_path_local="conf/pxe_cluster/dhcpd.conf"
 if os.path.exists(file_path_local):
	logger.info(file_path_local+" file exists")
	if os.path.exists("/etc/dhcp/dhcpd.conf"):
		logger.info(" /etc/dhcp/dhcpd.conf file exists , saving backup as dhcpd.conf.bkp")
		os.system('cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.bkp')
	logger.info("replacing file /etc/dhcp/dhcpd.conf ")
	os.system('cp conf/pxe_cluster/dhcpd.conf /etc/dhcp/')




def __addIscDhcpFile(pxeDict,subnet_list):
 """
 to  add interfaces in isc-dhcp-server  file
 :param config :
 :return
 """
 print" "
 logger.info("addIscDhcpFile function")

 file_path="conf/pxe_cluster/isc-dhcp-server"
 os.system('dos2unix '+file_path)
 if os.path.exists(file_path):
  logger.info(file_path+" file exists")
  all_interface=""

  for subnet in subnet_list:
     listen_iface = subnet.get('listen_iface')
     all_interface=all_interface+" "+str(listen_iface)

  all_interface=all_interface.strip()
  print all_interface
  __searchAndReplace(file_path,"INTERFACES","INTERFACES="+"\""+all_interface+"\"")
  if os.path.exists("/etc/default/isc-dhcp-server"):
   logger.info("/etc/default/isc-dhcp-server  file exists")
   os.system('echo '+pxeDict["password"] +' |  sudo -S cp /etc/default/isc-dhcp-server /etc/default/isc-dhcp-server.bkp')
   logger.info("saving backup as /etc/default/isc-dhcp-server.bkp")
  os.system('echo '+pxeDict["password"] +' |  sudo -S cp conf/pxe_cluster/isc-dhcp-server /etc/default/')


def __dhcpRestart():
 """
 to  restart dhcp server
 :param config : pxeDict
 :return
 """
 print" "
 logger.info("dhcpRestart function")
 os.system(' systemctl restart  isc-dhcp-server')
 os.system(' systemctl status  isc-dhcp-server')








def __ipmiPowerStatus(bmcIp,bmcUser,bmcPass):
 """
 to  get the status of bmc
 :param config : bmcIp,bmcUser,bmcPass
 :return
 """
 print" "
 logger.info("ipmiPowerStatus function")
 print bmcIp
 print bmcUser
 print bmcPass
 os.system('ipmitool -I lanplus -H '+bmcIp + ' -U '+bmcUser+'  -P '+bmcPass+'  chassis power status')




def __ipmiLanStatus(bmcIp,bmcUser,bmcPass):
 """
 to  get the status of lan
 :param config : bmcIp,bmcUser,bmcPass
 :return
 """
 print" "
 logger.info("ipmiLanStatus function")
 os.system('ipmitool -I lanplus -H '+bmcIp + ' -U '+bmcUser+'  -P '+bmcPass+'  lan print 1')



def __ipmiSetBootOrderPxe(bmcIp,bmcUser,bmcPass,order):
 """
 to set the boot order pxe
 :param config : bmcIp,bmcUser,bmcPass
 :return
 """
 print" "
 logger.info("ipmiSetBootOrderPxe function")
 os.system('ipmitool -I lanplus -H '+bmcIp + ' -U '+bmcUser+'  -P '+bmcPass+'  chassis bootdev '+ order)




def __ipmiRebootSystem(bmcIp,bmcUser,bmcPass):
 """
 to reboot the system via ipmi
 :param config : bmcIp,bmcUser,bmcPass
 :return
 """
 print" "
 logger.info("ipmiRebootSystem function")
 os.system('ipmitool -I lanplus -H '+bmcIp + ' -U '+bmcUser+'  -P '+bmcPass+'  chassis power cycle')


def __ipmiPowerOnSystem(bmcIp,bmcUser,bmcPass):
 """
 to power on the system via ipmi
 :param config : bmcIp,bmcUser,bmcPass
 :return
 """
 print" "
 logger.info("ipmiPowerOnSystem function")
 os.system('ipmitool -I lanplus -H '+bmcIp + ' -U '+bmcUser+'  -P '+bmcPass+'  chassis power on')


def __ipmiPowerOffSystem(bmcIp,bmcUser,bmcPass):
 """
 to power off the system via ipmi
 :param config : bmcIp,bmcUser,bmcPass
 :return
 """
 print" "
 logger.info("ipmiPowerOnSystem function")
 os.system('ipmitool -I lanplus -H '+bmcIp + ' -U '+bmcUser+'  -P '+bmcPass+'  chassis power off')


def __pxeBoot(bmcDict):
 """
 to start boot  via ipmi
 :param config :
 :return
 """
 print" "
 logger.info("pxeBoot function")
 #print bmcDict
 for host in bmcDict.get('host'):
	user=host.get('user')
	password=host.get('password')
	ip=host.get('ip')
	mac=host.get('mac')
	__ipmiPowerStatus(ip,user,password)
	__ipmiSetBootOrderPxe(ip,user,password, "pxe")
	__ipmiRebootSystem(ip,user,password)
def __pxeBootd(bmcDict):
 """
 to start boot  via disk
 :param config :
 :return
 """
 print" "
 logger.info("pxeBoot function")
 #print bmcDict
 for host in bmcDict.get('host'):
        user=host.get('user')
        password=host.get('password')
        ip=host.get('ip')
        mac=host.get('mac')
        __ipmiPowerStatus(ip,user,password)
        __ipmiSetBootOrderPxe(ip,user,password, "disk")
        __ipmiRebootSystem(ip,user,password)

def __provisionClean():
 """
 to clean the pxe server installation
 :param config :
 :return
 """
 print" "
 logger.info("provisionClean function")
 logger.info("stop isc-dhcp-server::systemctl stop isc-dhcp-server")
 os.system('systemctl stop isc-dhcp-server')
 logger.info("stop tftpd-hpa::systemctl stop tftpd-hpa")
 os.system('systemctl stop tftpd-hpa')
 os.system('rm -rf /var/lib/tftpboot/*')
 logger.info("removing tftpd")
 os.system('apt-get  -y remove tftpd-hpa ')
 os.system('apt-get  -y remove inetutils-inetd')
 logger.info("stop apache2::systemctl stop apache2")
 os.system('systemctl stop apache2')
 os.system('rm -rf /var/www/html/ubuntu')
 logger.info("removing apache2")
 os.system('apt-get  -y remove apache2')

 logger.info("removing dhcpServer")
 os.system('apt-get  -y remove isc-dhcp-server')
 logger.info("unmount mount point")
 os.system('umount  /mnt')

def __staticIPConfigure(staticDict,tftpDict,proxyDict):
 playbook_path="ansible_p/commission/hardware/playbooks/setIPConfig.yaml"
 playbook_path_bak="ansible_p/commission/hardware/playbooks/interfaceBak.yaml"
 host= staticDict.get('host')
 print "HOSTS---------------"
 print host
 valid= __validate_static_config(staticDict)
 if valid is False:
   logger.info("Configuration error please define IP for all the interface types")
   exit()
 http_proxy=proxyDict.get('http_proxy')
 https_proxy=proxyDict.get('https_proxy')
 print host[0]
 access_ip=None
 iplist=[]
 next_word=None
 with open("conf/pxe_cluster/ks.cfg") as openfile:
    for line in openfile:
        list_word=line.split()
        for part in line.split():
            if "rootpw" in part:
                next_word = list_word[list_word.index("rootpw") + 1]

 user_name=tftpDict.get('user')
 user_name='root'
 password=next_word
 check_dir=os.path.isdir(consts.SSH_PATH)
 if not check_dir:
   os.makedirs(consts.SSH_PATH)
 for i in range(len(host)):
  target=host[i].get('access_ip')
  iplist.append(target)
 consts.KEY_IP_LIST= iplist
 for i in range(len(host)):
  target=host[i].get('access_ip')
  subprocess.call('echo -e y|ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""', shell=True)
  command= "sshpass -p %s ssh-copy-id -o StrictHostKeyChecking=no %s@%s" %(password,user_name,target)
  subprocess.call(command,shell=True)
  interfaces=host[i].get('interfaces')
  backup_var="Y"
  ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_bak,{'target': target, 'bak': backup_var})
  for i in range(len(interfaces)):
   address=interfaces[i].get('address')
   gateway=interfaces[i].get('gateway')
   netmask=interfaces[i].get('netmask')
   iface=interfaces[i].get('iface')
   dns=interfaces[i].get('dns')
   dn=interfaces[i].get('dn')
   type=interfaces[i].get('type')
   ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path,{'target': target,'address': address, 'gateway': gateway, 'netmask': netmask, 'iface': iface, 'http_proxy': http_proxy, 'https_proxy': https_proxy, 'type': type, 'dns': dns, 'dn': dn})


def __staticIPCleanup(staticDict,tftpDict):
 playbook_path="ansible_p/commission/hardware/playbooks/delIPConfig.yaml"
 playbook_path_bak="ansible_p/commission/hardware/playbooks/interfaceBak.yaml"
 host= staticDict.get('host')
 access_ip=None
 iplist=[]
 next_word=None
 with open("conf/pxe_cluster/ks.cfg") as openfile:
    for line in openfile:
        list_word=line.split()
        for part in line.split():
            if "rootpw" in part:
                next_word = list_word[list_word.index("rootpw") + 1]

 user_name=tftpDict.get('user')
 user_name='root'
 #password=tftpDict.get('password')
 password=next_word
 check_dir=os.path.isdir(consts.SSH_PATH)
 if not check_dir:
   os.makedirs(consts.SSH_PATH)
 for i in range(len(host)):
  target=host[i].get('access_ip')
  iplist.append(target)
 print iplist
 for i in range(len(host)):
  target=host[i].get('access_ip')
  subprocess.call('echo -e y|ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""', shell=True)
  command= "sshpass -p %s ssh-copy-id -o StrictHostKeyChecking=no %s@%s" %(password,user_name,target)
  subprocess.call(command,shell=True)
  interfaces=host[i].get('interfaces')
  backup_var="N"
  ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path_bak,{'target': target, 'bak': backup_var})
  for i in range(len(interfaces)):
   address=interfaces[i].get('address')
   gateway=interfaces[i].get('gateway')
   netmask=interfaces[i].get('netmask')
   iface=interfaces[i].get('iface')
   dns=interfaces[i].get('dns')
   dn=interfaces[i].get('dn')
   type=interfaces[i].get('type')
   ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path,{'target': target,'address': address, 'gateway': gateway, 'netmask': netmask, 'iface': iface, 'type': type, 'dns': dns, 'dn': dn})

def __validate_static_config(staticDict):
   hosts= staticDict.get('host')
   valid=True
   for host in hosts:
      interfaces=host.get('interfaces')
      for interface in interfaces:
         if  interface.get('type')=='data'and interface.get('address') =="":
           valid=False
         if  interface.get('type')=='tenant'and interface.get('address')=="":
             valid=False
         if  interface.get('type')=='management'and interface.get('address')=="":
           valid=False
   return valid

def __setIsolCpus(tftpDict,cpuCoreDict):
 """
 to   set isolate cpu  in /etc/default/grub file
 :param config : tftpDict cpuCoreDict
 :return
 """
 logger.info("setIsolCpus function")
 iplist=[]
 rootPass=None
 with open("conf/pxe_cluster/ks.cfg") as openfile:
    for line in openfile:
        list_word=line.split()
        for part in line.split():
            if "rootpw" in part:
                rootPass = list_word[list_word.index("rootpw") + 1]
 user_name='root'
 playbook_path="ansible_p/commission/hardware/playbooks/setIsolCpus.yaml"
 host= cpuCoreDict.get('host')
 for ipCpu1 in host:
  target1=ipCpu1.get('ip')
  iplist.append(target1)

 for ipCpu in host:
   target=ipCpu.get('ip')
   isolcpus=ipCpu.get('isolcpus')
   hugepagesz=ipCpu.get('hugepagesz')
   hugepages=ipCpu.get('hugepages')
   if  isolcpus:
	logger.info("isolate cpu's for "+target+" are "+isolcpus)
	logger.info("hugepagesz for "+target +"  "+ hugepagesz)
	logger.info("hugepages for "+target +"  "+ hugepages)
   	subprocess.call('echo -e y|ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""', shell=True)
   	command= "sshpass -p %s ssh-copy-id -o StrictHostKeyChecking=no %s@%s" %(rootPass,user_name,target)
   	subprocess.call(command,shell=True)
   	ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path,{'target': target,'isolcpus': isolcpus,'hugepagesz': hugepagesz,'hugepages': hugepages})

def __delIsolCpus(tftpDict,cpuCoreDict):
 """
 to   set isolate cpu  in /etc/default/grub file
 :param config : tftpDict cpuCoreDict
 :return
 """
 logger.info("setIsolCpus function")
 iplist=[]
 rootPass=None
 with open("conf/pxe_cluster/ks.cfg") as openfile:
    for line in openfile:
        list_word=line.split()
        for part in line.split():
            if "rootpw" in part:
                rootPass = list_word[list_word.index("rootpw") + 1]
 user_name='root'
 playbook_path="ansible_p/commission/hardware/playbooks/delIsolCpus.yaml"
 host= cpuCoreDict.get('host')
 for ipCpu1 in host:
  target1=ipCpu1.get('ip')
  iplist.append(target1)

 for ipCpu in host:
   target=ipCpu.get('ip')
   isolcpus=ipCpu.get('isolcpus')
   hugepagesz=ipCpu.get('hugepagesz')
   hugepages=ipCpu.get('hugepages')
   if  isolcpus:
	logger.info("isolate cpu's for "+target+" are "+isolcpus)
	logger.info("hugepagesz for "+target +"  "+ hugepagesz)
	logger.info("hugepages for "+target +"  "+ hugepages)
   	subprocess.call('echo -e y|ssh-keygen -b 2048 -t rsa -f /root/.ssh/id_rsa -q -N ""', shell=True)
   	command= "sshpass -p %s ssh-copy-id -o StrictHostKeyChecking=no %s@%s" %(rootPass,user_name,target)
   	subprocess.call(command,shell=True)
   	ansible_playbook_launcher.__launch_ansible_playbook(iplist,playbook_path,{'target': target,'isolcpus': isolcpus,'hugepagesz': hugepagesz,'hugepages': hugepages})
