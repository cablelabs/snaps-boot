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

import pkg_resources

from snaps_common.ansible_snaps import ansible_utils

logger = logging.getLogger('deploy_venv')


def run(config, operation):
    prov_dict = config.get('PROVISION')
    proxy_dict = prov_dict.get('PROXY')
    tftp_dict = prov_dict.get('TFTP')
    static_dict = prov_dict.get('STATIC')
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

    if operation == "staticIPConfigure":
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


def __static_ip_configure(static_dict, proxy_dict):
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission', 'setIPConfig.yaml')
    playbook_path_bak = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission', 'interfaceBak.yaml')

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
        'snaps_boot.ansible_p.commission', 'delIPConfig.yaml')
    playbook_path_bak = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.commission', 'interfaceBak.yaml')

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
        'snaps_boot.ansible_p.commission', 'setIsolCpus.yaml')
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
        'snaps_boot.ansible_p.commission', 'delIsolCpus.yaml')
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
