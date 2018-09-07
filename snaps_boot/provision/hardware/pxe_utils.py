# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG SARL and Cable Television
# Laboratories, Inc.
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
import logging
import os.path
import re

import os
import pkg_resources

from snaps_boot.ansible_p.ansible_utils import ansible_playbook_launcher as apl

logger = logging.getLogger('deploy_venv')


def __main(config, operation):
    prov_dict = config.get('PROVISION')
    dhcp_dict = prov_dict.get('DHCP')
    proxy_dict = prov_dict.get('PROXY')
    pxe_dict = prov_dict.get('PXE')
    tftp_dict = prov_dict.get('TFTP')
    static_dict = prov_dict.get('STATIC')
    bmc_dict = prov_dict.get('BMC')
    subnet_list = dhcp_dict.get('subnet')
    cpu_core_dict = prov_dict.get('CPUCORE')
    pxe_config = tftp_dict.get('pxe_server_configuration')
    user_pass = None
    root_pass = None
    user_name = None
    build_pxe_server = None
    ubuntu_pxe_server = False
    centos_pxe_server = False
    ubuntu_dict = {}
    centos_dict = {}
    deprecated = False
    deprecated_info = {}
    if pxe_config is None:
        ubuntu_pxe_server = True
        build_pxe_server = "ubuntu"
        ubuntu_dict = tftp_dict
        deprecated = True
        deprecated_info['tftp'] = 'Missing pxe_server_configuration'
    else:
        for item in pxe_config:
            for key in item:
                if "ubuntu" == key:
                    ubuntu_pxe_server = True
                    build_pxe_server = "ubuntu"
                    ubuntu_dict = item.get("ubuntu")
                    user_pass = root_pass = ubuntu_dict["password"]
                    user_name = ubuntu_dict["user"]
                if "centos" == key:
                    centos_pxe_server = True
                    build_pxe_server = "centos"
                    centos_dict = item.get("centos")
                    user_pass = centos_dict["user_password"]
                    root_pass = centos_dict["root_password"]
                    user_name = centos_dict["user"]
    if ubuntu_pxe_server is True and centos_pxe_server is True:
        build_pxe_server = "ubuntu + centos"

    logger.info("buildPxeServer is :" + str(build_pxe_server))

    if operation == "hardware":
        __pxe_server_installation(proxy_dict, pxe_dict, ubuntu_dict,
                                  subnet_list, build_pxe_server, user_name,
                                  user_pass, root_pass)
        if (build_pxe_server == "centos"
                or build_pxe_server == "ubuntu + centos"):
            __centos_pxe_installation(pxe_dict, centos_dict, build_pxe_server)
            __validate_modify_centos_ks_cfg(pxe_dict, centos_dict, proxy_dict,
                                            build_pxe_server)
        # Handle deprecated file formats
        __configure_ng_cacher()
        if not proxy_dict.get("ngcacher_proxy"):
            deprecated = True
            deprecated_info['proxy'] = 'Missing ngcacher_proxy'
            proxy_dict['ngcacher_proxy'] = ""
        if proxy_dict.get("ngcacher_proxy") != "":
            __update_ng_cacher_proxy(proxy_dict)
    elif operation == "boot":
        if build_pxe_server == "ubuntu + centos":
            operation = "ubuntu"
            __modify_file_for_os(operation)
        __pxe_boot(bmc_dict)

    elif operation == "ubuntu":
        if build_pxe_server == "ubuntu + centos":
            __modify_file_for_os(operation)
            __pxe_boot(bmc_dict)
        elif build_pxe_server == "ubuntu":
            __pxe_boot(bmc_dict)
        else:
            logger.error('PXE SERVER IS CENTOS. UBUNTU CANNOT BE INSTALLED '
                         'ON HOST MACHINES')
            exit(1)

    elif operation == "centos":
        if build_pxe_server == "ubuntu + centos":
            __modify_file_for_os(operation)
            __pxe_boot(bmc_dict)
        elif build_pxe_server == "centos":
            __pxe_boot(bmc_dict)
        else:
            logger.error('PXE SERVER IS UBUNTU. CENTOS CANNOT BE INSTALLED '
                         'ON HOST MACHINES')
            exit(1)

    elif operation == "bootd":
        __pxe_bootd(bmc_dict)
    elif operation == "provisionClean":
        __provision_clean(proxy_dict)
    elif operation == "staticIPConfigure":
        __static_ip_configure(static_dict, proxy_dict)
    elif operation == "staticIPCleanup":
        __static_ip_cleanup(static_dict)
    elif operation == "setIsolCpus":
        __set_isol_cpus(cpu_core_dict)
    elif operation == "delIsolCpus":
        __del_isol_cpus(cpu_core_dict)
    else:
        logger.warn("Cannot read configuration")

    if deprecated is True:
        logger.warn("The Host.yaml file is a deprecated format, please "
                    "update ASAP")
    logger.warn(deprecated_info)


def __pxe_server_installation(proxy_dict, pxe_dict, ubuntu_dict, subnet_list,
                              build_pxe_server, user_name, user_pass,
                              root_pass):
    """
    This will launch the shell script to  install and configure dhcp , tftp
    and apache server.
    """
    logger.info("pxe_server_installation")
    logger.info("***********************set proxy**********************")
    os.system('sh scripts/PxeInstall.sh setProxy ' + proxy_dict["http_proxy"])
    logger.info("****************installPreReq ************************")
    os.system('sh scripts/PxeInstall.sh installPreReq ' + pxe_dict["password"])
    logger.info("****************dhcpInstall***************************")
    os.system('sh scripts/PxeInstall.sh dhcpInstall ' + proxy_dict[
        "http_proxy"] + " " + pxe_dict["password"])
    logger.info("*******dhcpConfigure iscDhcpServer*********************")
    __add_isc_dhcp_file(pxe_dict, subnet_list)
    logger.info("*******dhcpConfigure generate  dhcpd.conf file***********")
    __add_dhcpd_file(subnet_list)
    __move_dhcpd_file()
    logger.info("****************dhcpRestart****************************")
    __dhcp_restart()

    logger.info("****************ftpAndApacheInstall********************")
    os.system('sh scripts/PxeInstall.sh tftpAndApacheInstall ' + proxy_dict[
        "http_proxy"] + " " + pxe_dict["password"])
    logger.info("****************Create cloud-init files********************")
    __add_cloud_init_files(pxe_dict, subnet_list, user_name, user_pass,
                           root_pass)
    logger.info("**********tftpConfigure tftpdHpa***********************")
    os.system(
        'sh scripts/PxeInstall.sh tftpConfigure tftpdHpa' + " " + pxe_dict[
            "password"])
    logger.info("******************tftpdHpaRestart**********************")
    os.system(
        'sh scripts/PxeInstall.sh tftpdHpaRestart' + " "
        + pxe_dict["password"])
    if build_pxe_server == "ubuntu" or build_pxe_server == "ubuntu + centos":

        logger.info("******************mountAndCopy************************")
        os.system('sh scripts/PxeInstall.sh mountAndCopy ' + ubuntu_dict["os"]
                  + " " + pxe_dict["password"])
        logger.info("******************mountAndCopyUefi**********************")
        if "server_type" in ubuntu_dict and ubuntu_dict["server_type"] == "UEFI":
            os.system('sh scripts/PxeInstall.sh mountAndCopyUefi '
                      + 'grubnetx64.efi.signed'
                      + " " + "netboot.tar.gz" + " " + pxe_dict["password"])
        if build_pxe_server == "ubuntu + centos":
            logger.info("*************defaultFileConfigure*******************")
            os.system('sh scripts/PxeInstall.sh defaultFileConfigure ' +
                      pxe_dict["serverIp"] + " " + ubuntu_dict["seed"] + " " +
                      pxe_dict["password"])
        if build_pxe_server == "ubuntu":
            logger.info("**********defaultFileConfigureUbuntu***************")
            os.system('sh scripts/PxeInstall.sh defaultFileConfigureUbuntu ' +
                      pxe_dict["serverIp"] + " " + ubuntu_dict["seed"] + " " +
                      pxe_dict["password"])

        logger.info("*************bootMenuConfigure********************")
        os.system('sh scripts/PxeInstall.sh bootMenuConfigure ' + pxe_dict[
            "serverIp"] + " " + ubuntu_dict["seed"] + " " + pxe_dict[
            "password"])

        listen_iface = ""
        name = ""
        for subnet in subnet_list:
            listen_iface = subnet.get('listen_iface')
            name = subnet.get('name')

        logger.info("*********validateAndCreateconfigKsCfg****************")
        __create_ks_config(pxe_dict, ubuntu_dict, proxy_dict,
                           str(listen_iface))

        logger.info("*************defaultGrubConfigure********************")
        os.system('sh scripts/PxeInstall.sh defaultGrubConfigure '
                  + pxe_dict["serverIp"]
                  + " " + ubuntu_dict["seed"] + " " + str(name) + " "
                  + str(listen_iface)
                  + " " + pxe_dict["password"])

        logger.info("*********validateAndCreateconfigSeedIfUEFI*************")
        if ('server_type' in ubuntu_dict
                and ubuntu_dict['server_type'] == 'UEFI'):
            __create_seed_config(pxe_dict, ubuntu_dict, str(listen_iface))
            logger.info("*********validateAndCreateconfigPostScriptIfUEFI*************")
            __create_post_script_config(pxe_dict, ubuntu_dict, proxy_dict);

    logger.info("****************configureAnsibleFile*****************")
    __config_ansible_file()
    __config_ntp_server_file(pxe_dict)
    __restart_ntp_server(pxe_dict)


def __configure_ng_cacher():
    """
    used to configure acng.conf for ngcacher
    """
    logger.info("configuring apt-cacher-ng")
    __find_and_replace('/etc/apt-cacher-ng/acng.conf', "# PassThroughPattern: .* # this would allow CONNECT to everything",
                       " PassThroughPattern: .* # this would allow CONNECT to everything")
    os.system('systemctl restart apt-cacher-ng') 

def __create_ks_config(pxe_dict, ubuntu_dict, proxy_dict, boot_interface):
    """
    used to configure ks.cfg from hosts.yaml file
    :param pxe_dict:
    :param ubuntu_dict:
    :param proxy_dict:
    :param boot_interface:
    """
    os.system('dos2unix conf/pxe_cluster/ks.cfg')
    logger.info("configuring   timezone in ks.cfg")
    __find_and_replace('conf/pxe_cluster/ks.cfg', "timezone",
                       "timezone  " + ubuntu_dict["timezone"])

    logger.debug("configuring   client user password   name in ks.cfg")
    user_creds = "user " + ubuntu_dict["user"] + " --fullname " + ubuntu_dict[
        "fullname"] + " --password " + ubuntu_dict["password"]
    __find_and_replace('conf/pxe_cluster/ks.cfg', "user", user_creds)

    logger.debug("configuring   client root password   name in ks.cfg")
    user_creds = "rootpw " + ubuntu_dict["password"]
    __find_and_replace('conf/pxe_cluster/ks.cfg', "rootpw", user_creds)

    logger.debug("configuring server url  in ks.cfg")
    my_url = "url --url http://" + pxe_dict["serverIp"] + "/ubuntu/"
    __find_and_replace('conf/pxe_cluster/ks.cfg', "url", my_url)

    logger.debug("configuring ntp server ip  in ks.cfg")
    ntp_server = "server " + pxe_dict["serverIp"] + " iburst"
    __find_and_replace('conf/pxe_cluster/ks.cfg', "server", ntp_server)

    if 'server_type' in ubuntu_dict and ubuntu_dict['server_type'] == 'UEFI':
        logger.debug("removing partition from ks.cfg for UEFI")
        __find_and_replace(
            'conf/pxe_cluster/ks.cfg',
            "part / --fstype ext4 --size 1 --grow --asprimary", "")

    logger.debug("configuring cloud-init server ip  in ks.cfg")
    cloud_init_ip = "CLOUD_INIT_IP=" + pxe_dict["serverIp"]
    __find_and_replace('conf/pxe_cluster/ks.cfg',
                       "CLOUD_INIT_IP=cloud-init-ip",
                       cloud_init_ip)

    logger.debug("configuring cloud-init server ip  in ks.cfg")
    cloud_init_ip = "CLOUD_INIT_IP=" + pxe_dict["serverIp"]
    __find_and_replace('conf/pxe_cluster/ks.cfg',
                       "CLOUD_INIT_IP=cloud-init-ip",
                       cloud_init_ip)

    logger.debug("configuring boot interface in ks.cfg")
    boot_iface = "network --bootproto=dhcp --device=" + boot_interface
    __find_and_replace('conf/pxe_cluster/ks.cfg', "network", boot_iface)

    logger.debug("configuring http proxy  in ks.cfg")
    http_proxy = "Acquire::http::Proxy " + "\"" \
                 + proxy_dict["http_proxy"] + "\";"
    __find_and_replace('conf/pxe_cluster/ks.cfg', "Acquire::http::Proxy",
                       http_proxy)

    logger.debug("configuring https proxy  in ks.cfg")
    https_proxy = "Acquire::https::Proxy " + "\"" \
                  + proxy_dict["https_proxy"] + "\";"
    __find_and_replace('conf/pxe_cluster/ks.cfg', "Acquire::https::Proxy",
                       https_proxy)

    logger.debug("configuring ftp proxy  in ks.cfg")
    ftp_proxy = "Acquire::ftp::Proxy " + "\"" + proxy_dict["ftp_proxy"] + "\";"
    __find_and_replace('conf/pxe_cluster/ks.cfg', "Acquire::ftp::Proxy",
                       ftp_proxy)

    logger.debug("copy local ks.cfg to location /var/www/html/ubuntu/")
    os.system('cp conf/pxe_cluster/ks.cfg /var/www/html/ubuntu/')


def __create_seed_config(pxe_dict, ubuntu_dict, boot_interface):
    """
    used to configure seed file from hosts.yaml file
    :param pxe_dict:
    :param ubuntu_dict:
    :param boot_interface:
    """
    os.system('dos2unix conf/pxe_cluster/ubuntu-uefi-server.seed')

    logger.debug("configuring server url  in ubuntu-uefi-server.seed")
    my_url = "d-i mirror/http/hostname string " + pxe_dict["serverIp"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i mirror/http/hostname string 192.168.0.1",
                       my_url)

    logger.debug("configuring boot interface in ubuntu-uefi-server.seed")
    boot_iface = "d-i netcfg/choose_interface select " + boot_interface
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i netcfg/choose_interface select en0",
                       boot_iface)

    logger.debug("configuring ntp in ubuntu-uefi-server.seed")
    ntp_server = "d-i clock-setup/ntp-server string " + pxe_dict["serverIp"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i clock-setup/ntp-server string 192.168.0.1",
                       ntp_server)

    logger.debug("configuring client user fullname in ubuntu-uefi-server.seed")
    user_creds = "d-i passwd/user-fullname string " + ubuntu_dict["fullname"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i passwd/user-fullname string Ubuntu User",
                       user_creds)

    logger.debug("configuring client username in ubuntu-uefi-server.seed")
    user_creds = "d-i passwd/username string " + ubuntu_dict["user"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i passwd/username string ubuntu", user_creds)

    logger.debug("configuring client user password in ubuntu-uefi-server.seed")
    user_creds = "d-i passwd/user-password password "\
                 + ubuntu_dict["password"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i passwd/user-password password ChangeMe123",
                       user_creds)

    logger.debug("configuring client user password verify in "
                 "ubuntu-uefi-server.seed")
    user_creds = "d-i passwd/user-password-again password "\
                 + ubuntu_dict["password"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i passwd/user-password-again password ChangeMe123",
                       user_creds)

    logger.debug("configuring client root password in "
                 "ubuntu-uefi-server.seed")
    user_creds = "d-i passwd/root-password password "\
                 + ubuntu_dict["password"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i passwd/user-password password ChangeMe123",
                       user_creds)

    logger.debug("configuring client root password verify in "
                 "ubuntu-uefi-server.seed")
    user_creds = "d-i passwd/root-password-again password "\
                 + ubuntu_dict["password"]
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "d-i passwd/user-password-again password ChangeMe123",
                       user_creds)

    logger.debug("configuring late command script in "
                 "ubuntu-uefi-server.seed")
    post_command = "http://" + pxe_dict["serverIp"] + "/ubuntu/post.sh | \\"
    __find_and_replace('conf/pxe_cluster/ubuntu-uefi-server.seed',
                       "    http://192.168.0.1/ubuntu/post.sh",
                       post_command)

    logger.debug("copy local ubuntu-uefi-server.seed to location "
                 "/var/www/html/ubuntu/preseed")
    os.system('cp conf/pxe_cluster/ubuntu-uefi-server.seed '
              '/var/www/html/ubuntu/preseed')



def __create_post_script_config(pxe_dict, ubuntu_dict, proxy_dict):
    """
    used to configure seed file from hosts.yaml file
    :param pxe_dict:
    :param ubuntu_dict:
    :param proxy_dict:
    """
    os.system('dos2unix conf/pxe_cluster/post.sh')



    logger.debug("configuring ntp server ip  in post.sh")
    ntp_server = "server " + pxe_dict["serverIp"] + " iburst"
    __find_and_replace('conf/pxe_cluster/post.sh', "server", ntp_server)

    logger.debug("configuring cloud-init server ip  in post.sh")
    cloud_init_ip = "CLOUD_INIT_IP=" + pxe_dict["serverIp"]
    __find_and_replace('conf/pxe_cluster/post.sh',
                       "CLOUD_INIT_IP=cloud-init-ip",
                       cloud_init_ip)

    logger.debug("configuring http proxy  in post.sh")
    http_proxy = "Acquire::http::Proxy " + "\"" \
                 + proxy_dict["http_proxy"] + "\";"
    __find_and_replace('conf/pxe_cluster/post.sh', "Acquire::http::Proxy",
                       http_proxy)

    logger.debug("configuring https proxy  in post.sh")
    https_proxy = "Acquire::https::Proxy " + "\"" \
                  + proxy_dict["https_proxy"] + "\";"
    __find_and_replace('conf/pxe_cluster/post.sh', "Acquire::https::Proxy",
                       https_proxy)

    logger.debug("configuring ftp proxy  in post.sh")
    ftp_proxy = "Acquire::ftp::Proxy " + "\"" + proxy_dict["ftp_proxy"] + "\";"
    __find_and_replace('conf/pxe_cluster/post.sh', "Acquire::ftp::Proxy",
                       ftp_proxy)

    logger.debug("copy local post.sh to location /var/www/html/ubuntu/")
    os.system('cp conf/pxe_cluster/post.sh /var/www/html/ubuntu/')



def __find_and_replace(fname, pat, s_after):
    """
    search a line start with pat in file fname  and replace that whole line by
    string s_after
    :param fname: filename
    :param pat: string to search a line start with
    :param s_after: string to replace the line
    :return
    """
    # first, see if the pattern is even in the file.
    # if line start with pat, then replace  whole line by subst
    with open(fname) as f:
        out_fname = fname + ".tmp"
        out = open(out_fname, "w")
        for line in f:
            if re.match(pat, line):
                logger.info("changing pattern " + pat + " --> " + s_after)
                line = s_after + "\n"
            out.write(line)
        out.close()
        os.rename(out_fname, fname)


def __config_ansible_file():
    """
    to uncomment host_key_checking field in ansible.cfg file
    """
    logger.info("configureAnsibleFile function")
    file_path = "/etc/ansible/ansible.cfg"
    os.system('dos2unix ' + file_path)
    if os.path.exists(file_path):
        logger.info(file_path + " file exists")
        __find_and_replace(file_path, "#host_key_checking",
                           "host_key_checking = False")


def __config_ntp_server_file(pxe_dict):
    """
    to  configure   ntp.conf file
    :param pxe_dict:
    """
    logger.info("configureNTPServerFile function")
    file_path = "/etc/ntp.conf"
    os.system('dos2unix ' + file_path)
    if os.path.exists(file_path):
        logger.info(file_path + " file exists")
        os.system('echo ' + pxe_dict[
            "password"] + ' | sudo -S cp /etc/ntp.conf /etc/ntp.conf_bkp')
        __find_and_replace(file_path, "pool 0.ubuntu.pool.ntp.org iburst",
                           "#pool 0.ubuntu.pool.ntp.org iburst")
        __find_and_replace(file_path, "pool 1.ubuntu.pool.ntp.org iburst",
                           "#pool 1.ubuntu.pool.ntp.org iburst")
        __find_and_replace(file_path, "pool 2.ubuntu.pool.ntp.org iburst",
                           "#pool 2.ubuntu.pool.ntp.org iburst")
        __find_and_replace(file_path, "pool 3.ubuntu.pool.ntp.org iburst",
                           "#pool 3.ubuntu.pool.ntp.org iburst")
        __find_and_replace(file_path, "pool ntp.ubuntu.com",
                           "#pool ntp.ubuntu.com")
        __find_and_replace(file_path, "#server 127.127.22.1",
                           "server 127.127.1.0 prefer")


def __restart_ntp_server(pxe_dict):
    """
    to restart ntp server
    :param pxe_dict
    """
    logger.info("restartNTPServer function")
    os.system('echo ' + pxe_dict[
        "password"] + ' |  sudo -S systemctl restart  ntp.service')
    os.system('echo ' + pxe_dict[
        "password"] + ' |  sudo -S systemctl status  ntp.service')


def __add_dhcpd_file(subnet_list):
    """
    to generate local dhcpd.conf file
    """
    logger.info("addDhcpdFile function")
    common_str = """
 ddns-update-style none;
 default-lease-time 1600;
 max-lease-time 7200;
 authoritative;
 log-facility local7;
 allow booting;
 allow bootp;
 option option-128 code 128 = string;
 option option-129 code 129 = text;
 option vendor-class code 60 = string;
 option arch code 93 = unsigned integer 16;
 #next-server X.X.X.X;
 class "pxeclient" {
    match if substring (option vendor-class-identifier, 0, 9) = "PXEClient";
    if option arch = 00:07 {
        filename "grubnetx64.efi.signed";
    }
    else {
        filename "pxelinux.0";
    }
 }
 """

    file_path = "conf/pxe_cluster/dhcpd.conf"
    os.system('dos2unix ' + file_path)
    if os.path.exists(file_path):
        logger.info(file_path + " file exists")
        os.system(
            'cp conf/pxe_cluster/dhcpd.conf conf/pxe_cluster/dhcpd.conf.bkp')
    with open(file_path, "w") as text_file:
        text_file.write(common_str)
        text_file.write("\n")
        for subnet in subnet_list:
            address = subnet.get('address')
            subnet_range = subnet.get('range')
            netmask = subnet.get('netmask')
            router = subnet.get('router')
            broadcast = subnet.get('broadcast-address')
            default_lease = subnet.get('default-lease')
            max_lease = subnet.get('max-lease')
            dns = subnet.get('dns')
            dn = subnet.get('dn')
            subnet_d = "subnet " + address + " netmask " + netmask \
                       + "{" + "\n" + "  range " + subnet_range + ";" + "\n" \
                       + "  option domain-name-servers " + dns + ";" + "\n" \
                       + "  option domain-name \"" + dn + "\";" + "\n" \
                       + "  option subnet-mask " + netmask + ";" + "\n" \
                       + "  option routers " + router + ";" + "\n" \
                       + "  option broadcast-address " + broadcast + ";" \
                       + "\n" + "  default-lease-time " + str(default_lease) \
                       + ";" + "\n" + "  max-lease-time " + str(max_lease) \
                       + ";" + "\n" + "  deny unknown-clients;" + "\n" + "}"
            text_file.write(subnet_d)
            text_file.write("\n")

            mac_ip_list = subnet.get('bind_host')
            for mac_ip in mac_ip_list:
                host_sub = "host ubuntu-client-" + mac_ip.get(
                    'ip') + " {" + "\n" + "  hardware ethernet " + mac_ip.get(
                    'mac') + ";" + "\n" + "  fixed-address " + mac_ip.get(
                    'ip') + ";" + "\n" + "}"
                text_file.write(host_sub)
                text_file.write("\n")


def __add_cloud_init_files(pxe_dict, subnet_list, user_name, user_pass,
                           root_pass):
    """
    Create cloud init files on the web server for each traget node
    """
    playbook_path = pkg_resources.resource_filename(
      'snaps_boot.ansible_p.commission.hardware.playbooks',
      'create_cloud_config.yaml')
    mac_list = []
    for subnet in subnet_list:
        mac_ip_list = subnet.get('bind_host')
        for mac_ip in mac_ip_list:
            mac_list.append(mac_ip.get('mac'))

    iplist = [pxe_dict.get('serverIp')]
    apl.__launch_ansible_playbook(
        iplist, playbook_path, {
            'target': ["localhost"],
            'target_macs': mac_list,
            'user_pass': user_pass,
            'user_name': user_name,
            'root_pass': root_pass})


def __move_dhcpd_file():
    """
    to  move local dhcpd  file
    """
    logger.info("moveDhcpdFile function")
    file_path_local = "conf/pxe_cluster/dhcpd.conf"
    if os.path.exists(file_path_local):
        logger.info(file_path_local + " file exists")
        if os.path.exists("/etc/dhcp/dhcpd.conf"):
            logger.info(
                '/etc/dhcp/dhcpd.conf file exists,'
                ' saving backup as dhcpd.conf.bkp')
            os.system('cp /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.bkp')
        logger.info("replacing file /etc/dhcp/dhcpd.conf ")
        os.system('cp conf/pxe_cluster/dhcpd.conf /etc/dhcp/')


def __add_isc_dhcp_file(pxe_dict, subnet_list):
    """
    to  add interfaces in isc-dhcp-server  file
    """
    logger.info("addIscDhcpFile function")

    file_path = "conf/pxe_cluster/isc-dhcp-server"
    os.system('dos2unix ' + file_path)
    if os.path.exists(file_path):
        logger.info(file_path + " file exists")
        all_interface = ""

        for subnet in subnet_list:
            listen_iface = subnet.get('listen_iface')
            all_interface = all_interface + " " + str(listen_iface)

        all_interface = all_interface.strip()
        __find_and_replace(file_path, "INTERFACES",
                           "INTERFACES=" + "\"" + all_interface + "\"")
        if os.path.exists("/etc/default/isc-dhcp-server"):
            logger.info("/etc/default/isc-dhcp-server  file exists")
            os.system(
                'echo ' + pxe_dict["password"]
                + ' |  sudo -S cp /etc/default/isc-dhcp-server /etc/default'
                  '/isc-dhcp-server.bkp')
            logger.info("saving backup as /etc/default/isc-dhcp-server.bkp")
        os.system(
            'echo ' + pxe_dict["password"]
            + ' |  sudo -S cp conf/pxe_cluster/isc-dhcp-server /etc/default/')


def __dhcp_restart():
    """
    to  restart dhcp server
    """
    logger.info("dhcpRestart function")
    os.system(' systemctl restart  isc-dhcp-server')
    os.system(' systemctl status  isc-dhcp-server')


def __ipmi_power_status(bmc_ip, bmc_user, bmc_pass):
    """
    to  get the status of bmc
    """
    logger.info("ipmiPowerStatus function")
    os.system(
        'ipmitool -I lanplus -H ' + bmc_ip + ' -U ' + bmc_user + '  -P '
        + bmc_pass + '  chassis power status')


def __ipmi_lan_status(bmc_ip, bmc_user, bmc_pass):
    """
    to  get the status of lan
    """
    logger.info("ipmiLanStatus function")
    os.system(
        'ipmitool -I lanplus -H ' + bmc_ip + ' -U ' + bmc_user + '  -P '
        + bmc_pass + '  lan print 1')


def __ipmi_set_boot_order_pxe(bmc_ip, bmc_user, bmc_pass, order):
    """
    to set the boot order pxe
    """
    logger.info("ipmiSetBootOrderPxe function")
    os.system(
        'ipmitool -I lanplus -H ' + bmc_ip + ' -U ' + bmc_user + '  -P '
        + bmc_pass + '  chassis bootdev ' + order)


def __ipmi_reboot_system(bmc_ip, bmc_user, bmc_pass):
    """
    to reboot the system via ipmi
    """
    logger.info("ipmiRebootSystem function")
    os.system(
        'ipmitool -I lanplus -H ' + bmc_ip + ' -U ' + bmc_user + '  -P '
        + bmc_pass + '  chassis power cycle')


def __ipmi_power_on_system(bmc_ip, bmc_user, bmc_pass):
    """
    to power on the system via ipmi
    """
    logger.info("ipmiPowerOnSystem function")
    os.system(
        'ipmitool -I lanplus -H ' + bmc_ip + ' -U ' + bmc_user + '  -P '
        + bmc_pass + '  chassis power on')


def __ipmi_power_off_system(bmc_ip, bmc_user, bmc_pass):
    """
    to power off the system via ipmi
    """
    logger.info("ipmiPowerOnSystem function")
    os.system(
        'ipmitool -I lanplus -H ' + bmc_ip + ' -U ' + bmc_user + '  -P '
        + bmc_pass + '  chassis power off')


def __pxe_boot(bmc_dict):
    """
    to start boot via ipmi
    """
    logger.info("pxeBoot function")
    for host in bmc_dict.get('host'):
        user = host.get('user')
        password = host.get('password')
        ip = host.get('ip')
        __ipmi_power_status(ip, user, password)
        __ipmi_set_boot_order_pxe(ip, user, password, "pxe")
        __ipmi_reboot_system(ip, user, password)


def __pxe_bootd(bmc_dict):
    """
    to start boot  via disk
    """
    logger.info("pxeBoot function")
    for host in bmc_dict.get('host'):
        user = host.get('user')
        password = host.get('password')
        ip = host.get('ip')
        __ipmi_power_status(ip, user, password)
        __ipmi_set_boot_order_pxe(ip, user, password, "disk")
        __ipmi_reboot_system(ip, user, password)


def __provision_clean(proxy_dict):
    """
    to clean the pxe server installation
    """
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

    if "ngcacher_proxy" in proxy_dict and proxy_dict["ngcacher_proxy"] != "":
        __clean_ngcacher_proxy(proxy_dict)


def __static_ip_configure(static_dict, proxy_dict):
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission.hardware.playbooks',
        'setIPConfig.yaml')
    playbook_path_bak = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission.hardware.playbooks',
        'interfaceBak.yaml')

    host = static_dict.get('host')
    valid = __validate_static_config(static_dict)
    if valid is False:
        logger.info(
            "Configuration error please define IP for all the interface types")
        exit()
    http_proxy = proxy_dict.get('http_proxy')
    https_proxy = proxy_dict.get('https_proxy')
    iplist = []

    for this_host in host:
        target = this_host.get('access_ip')
        iplist.append(target)
    for host_counter in host:
        target = host_counter.get('access_ip')

        interfaces = host_counter.get('interfaces')
        backup_var = "Y"
        apl.__launch_ansible_playbook(
            iplist, playbook_path_bak, {'target': target, 'bak': backup_var})

        for interface in interfaces:
            address = interface.get('address')
            gateway = interface.get('gateway')
            netmask = interface.get('netmask')
            iface = interface.get('iface')
            dns = interface.get('dns')
            dn = interface.get('dn')
            intf_type = interface.get('type')
            apl.__launch_ansible_playbook(
                iplist, playbook_path, {
                    'target': target,
                    'address': address,
                    'gateway': gateway,
                    'netmask': netmask,
                    'iface': iface,
                    'http_proxy': http_proxy,
                    'https_proxy': https_proxy,
                    'type': intf_type,
                    'dns': dns,
                    'dn': dn})


def __static_ip_cleanup(static_dict):
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission.hardware.playbooks',
        'delIPConfig.yaml')
    playbook_path_bak = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission.hardware.playbooks',
        'interfaceBak.yaml')

    host = static_dict.get('host')
    iplist = []

    for this_host in host:
        iplist.append(this_host.get('access_ip'))
    for host_counter in host:
        target = host_counter.get('access_ip')
        interfaces = host_counter.get('interfaces')
        backup_var = "N"
        apl.__launch_ansible_playbook(
            iplist, playbook_path_bak, {'target': target, 'bak': backup_var})

        for interface in interfaces:
            address = interface.get('address')
            gateway = interface.get('gateway')
            netmask = interface.get('netmask')
            iface = interface.get('iface')
            dns = interface.get('dns')
            dn = interface.get('dn')
            intf_type = interface.get('type')
            apl.__launch_ansible_playbook(
                iplist, playbook_path, {
                    'target': target,
                    'address': address,
                    'gateway': gateway,
                    'netmask': netmask,
                    'iface': iface,
                    'type': intf_type,
                    'dns': dns,
                    'dn': dn})


def __validate_static_config(static_dict):
    hosts = static_dict.get('host')
    valid = True
    for host in hosts:
        interfaces = host.get('interfaces')
        for interface in interfaces:
            if interface.get('type') == 'data' and interface.get(
                    'address') == "":
                valid = False
            if interface.get('type') == 'tenant' and interface.get(
                    'address') == "":
                valid = False
            if interface.get('type') == 'management' and interface.get(
                    'address') == "":
                valid = False
    return valid


def __set_isol_cpus(cpu_core_dict):
    """
    to   set isolate cpu  in /etc/default/grub file
    """
    logger.info("setIsolCpus function")
    iplist = []
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission.hardware.playbooks',
        'setIsolCpus.yaml')
    host = cpu_core_dict.get('host')
    for ipCpu1 in host:
        target1 = ipCpu1.get('ip')
        iplist.append(target1)

    for ipCpu in host:
        target = ipCpu.get('ip')
        isolcpus = ipCpu.get('isolcpus')
        hugepagesz = ipCpu.get('hugepagesz')
        hugepages = ipCpu.get('hugepages')
        if isolcpus:
            logger.info("isolate cpu's for " + target + " are " + isolcpus)
            logger.info("hugepagesz for " + target + "  " + hugepagesz)
            logger.info("hugepages for " + target + "  " + hugepages)
            apl.__launch_ansible_playbook(
                iplist, playbook_path, {
                    'target': target,
                    'isolcpus': isolcpus,
                    'hugepagesz': hugepagesz,
                    'hugepages': hugepages})


def __del_isol_cpus(cpu_core_dict):
    """
    to set isolate cpu  in /etc/default/grub file
    """
    logger.info("setIsolCpus function")
    iplist = []
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission.hardware.playbooks',
        'delIsolCpus.yaml')
    host = cpu_core_dict.get('host')
    for ipCpu1 in host:
        target1 = ipCpu1.get('ip')
        iplist.append(target1)

    for ipCpu in host:
        target = ipCpu.get('ip')
        isolcpus = ipCpu.get('isolcpus')
        hugepagesz = ipCpu.get('hugepagesz')
        hugepages = ipCpu.get('hugepages')
        if isolcpus:
            logger.info("isolate cpu's for " + target + " are " + isolcpus)
            logger.info("hugepagesz for " + target + "  " + hugepagesz)
            logger.info("hugepages for " + target + "  " + hugepages)
            apl.__launch_ansible_playbook(
                iplist, playbook_path, {
                    'target': target,
                    'isolcpus': isolcpus,
                    'hugepagesz': hugepagesz,
                    'hugepages': hugepages})


def __centos_pxe_installation(pxe_dict, centos_dict, build_pxe_server):
    iplist = []
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission.hardware.playbooks',
        'centos_pxe.yaml')
    iso_name = centos_dict.get('os')
    boot_disk = centos_dict.get('boot_disk')
    if boot_disk is None:
        boot_disk = "sda"
    iplist.append(pxe_dict.get('serverIp'))
    apl.__launch_ansible_playbook(
        iplist, playbook_path, {
            'isoName': iso_name,
            'pxeServer': build_pxe_server,
            'bootDisk': boot_disk,
            'cloudInitIp': iplist[0]})


def __validate_modify_centos_ks_cfg(pxe_dict, centos_dict, proxy_dict,
                                    build_pxe_server):
    """
    used to configure ks.cfg file
    :param pxe_dict
    :parma centos_dict
    :proxy_dict
    :build_build_pxe_server
    :return
    """

    logger.info("configuring   timezone in ks.cfg")
    __find_and_replace('/var/www/centos7/ks.cfg', "timezone", "timezone " +
                       centos_dict["timezone"])

    logger.debug("configuring   client user password   name in ks.cfg")
    user_credentials = "user --name=" + centos_dict["user"] + " --password=" +\
                       centos_dict["user_password"] + " --gecos=" + "\"" +\
                       centos_dict["user"] + "\""
    __find_and_replace('/var/www/centos7/ks.cfg', "user", user_credentials)

    logger.debug("configuring   client root password   name in ks.cfg")
    user_credentials = "rootpw " + centos_dict["root_password"]
    __find_and_replace('/var/www/centos7/ks.cfg', "rootpw", user_credentials)

    logger.debug("configuring server url  in ks.cfg")
    my_url = "url --url=" + "\"http://" + pxe_dict["serverIp"] + ":/centos7" +\
             "\""
    __find_and_replace('/var/www/centos7/ks.cfg', "url", my_url)

    logger.debug("configuring ntp server ip  in ks.cfg")
    ntp_server = "server " + pxe_dict["serverIp"] + " iburst"
    __find_and_replace('/var/www/centos7/ks.cfg', "server", ntp_server)

    logger.debug("configuring http proxy  in ks.cfg")
    http_proxy = "proxy=" + proxy_dict["http_proxy"]
    __find_and_replace('/var/www/centos7/ks.cfg', "#proxy=http:", http_proxy)

    if "https_proxy" in proxy_dict and proxy_dict["https_proxy"] != "":
        logger.debug("configuring https proxy  in ks.cfg")
        https_proxy = "proxy=" + proxy_dict["https_proxy"]
        __find_and_replace('/var/www/centos7/ks.cfg', "#proxy=https:",
                           https_proxy)

    if "ftp_proxy" in proxy_dict and proxy_dict["ftp_proxy"] != "":
        logger.debug("configuring ftp proxy  in ks.cfg")
        ftp_proxy = "proxy=" + proxy_dict["ftp_proxy"]
        __find_and_replace('/var/www/centos7/ks.cfg', "#proxy=ftp", ftp_proxy)

    if build_pxe_server == "centos":
        __modify_ip_in_pxelinux(pxe_dict)


def __modify_file_for_os(operation):
    os_to_be_installed = operation
    if os_to_be_installed == "centos":
        logger.debug("configuring ftp proxy  in ks.cfg")
        value = "ONTIMEOUT centos"
        __find_and_replace(
            '/var/lib/tftpboot/ubuntu-installer/amd64/pxelinux.cfg/default',
            "ONTIMEOUT", value)
    elif os_to_be_installed == "ubuntu":
        logger.debug("configuring ftp proxy  in ks.cfg")
        value = "ONTIMEOUT ubuntu"
        __find_and_replace(
            '/var/lib/tftpboot/ubuntu-installer/amd64/pxelinux.cfg/default',
            "ONTIMEOUT", value)


def __modify_ip_in_pxelinux(pxe_dict):
    value = "append initrd=centos7/initrd.img ks=http://"\
            + pxe_dict["serverIp"] + ":/centos7/ks.cfg"
    __find_and_replace('/var/lib/tftpboot/pxelinux.cfg/default',
                       "append initrd", value)


def __update_ng_cacher_proxy(proxy_dict):
    value1 = "Proxy: " + proxy_dict["ngcacher_proxy"]
    value2 = "VfilePatternEx: {}|{}|{}".format(
        '^(/\?release=[0-9]+&arch=.*',
        '.*/RPM-GPG-KEY-.*',
        '/metalink\?repo=epel\-[0-9]+&arch=.*)$')
    __find_and_replace(
        '/etc/apt-cacher-ng/acng.conf',
        "# Proxy: https://username:proxypassword@proxy.example.net:3129",
        value1)
    __find_and_replace('/etc/apt-cacher-ng/acng.conf',
                       "#VfilePatternEx: /centos/treeinfo", value2)
    os.system(' systemctl restart  apt-cacher-ng')


def __clean_ngcacher_proxy(proxy_dict):
    value1 = "Proxy: " + proxy_dict["ngcacher_proxy"]
    __find_and_replace(
        '/etc/apt-cacher-ng/acng.conf', value1,
        "# Proxy: https://username:proxypassword@proxy.example.net:3129")
    __find_and_replace('/etc/apt-cacher-ng/acng.conf', "VfilePatternEx:",
                       "#VfilePatternEx: /centos/treeinfo")
    os.system(' systemctl restart  apt-cacher-ng')
