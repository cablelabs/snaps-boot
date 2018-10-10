# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG SARL
# and Cable Television Laboratories, Inc.
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

from snaps_common.ansible_snaps import ansible_utils

logger = logging.getLogger('deploy_venv')


def run(config, operation):
    prov_dict = config.get('PROVISION')
    proxy_dict = prov_dict.get('PROXY')
    tftp_dict = prov_dict.get('TFTP')
    static_dict = prov_dict.get('STATIC')
    bmc_dict = prov_dict.get('BMC')
    cpu_core_dict = prov_dict.get('CPUCORE')
    pxe_config = tftp_dict.get('pxe_server_configuration')
    build_pxe_server = None
    ubuntu_pxe_server = False
    centos_pxe_server = False
    deprecated = False
    deprecated_info = {}
    if pxe_config is None:
        ubuntu_pxe_server = True
        build_pxe_server = "ubuntu"
        deprecated = True
        deprecated_info['tftp'] = 'Missing pxe_server_configuration'
    else:
        for item in pxe_config:
            for key in item:
                if "ubuntu" == key:
                    ubuntu_pxe_server = True
                    build_pxe_server = "ubuntu"
                if "centos" == key:
                    centos_pxe_server = True
                    build_pxe_server = "centos"
    if ubuntu_pxe_server is True and centos_pxe_server is True:
        build_pxe_server = "ubuntu + centos"

    logger.info("buildPxeServer is :" + str(build_pxe_server))

    if operation == "boot":
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


def __ipmi_power_status(bmc_ip, bmc_user, bmc_pass):
    """
    to  get the status of bmc
    """
    logger.info("ipmiPowerStatus function")
    os.system(
        'ipmitool -I lanplus -H ' + bmc_ip + ' -U ' + bmc_user + '  -P '
        + bmc_pass + '  chassis power status')


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
        ansible_utils.apply_playbook(
            playbook_path_bak, iplist,
            variables={'target': target, 'bak': backup_var})

        for interface in interfaces:
            address = interface.get('address')
            gateway = interface.get('gateway')
            netmask = interface.get('netmask')
            iface = interface.get('iface')
            dns = interface.get('dns')
            dn = interface.get('dn')
            intf_type = interface.get('type')
            ansible_utils.apply_playbook(playbook_path, iplist, variables={
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
        ansible_utils.apply_playbook(
            playbook_path_bak, iplist,
            variables={'target': target, 'bak': backup_var})

        for interface in interfaces:
            address = interface.get('address')
            gateway = interface.get('gateway')
            netmask = interface.get('netmask')
            iface = interface.get('iface')
            dns = interface.get('dns')
            dn = interface.get('dn')
            intf_type = interface.get('type')
            ansible_utils.apply_playbook(playbook_path, iplist, variables={
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
            ansible_utils.apply_playbook(playbook_path, iplist, variables={
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
            ansible_utils.apply_playbook(playbook_path, iplist, variables={
                'target': target,
                'isolcpus': isolcpus,
                'hugepagesz': hugepagesz,
                'hugepages': hugepages})


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
