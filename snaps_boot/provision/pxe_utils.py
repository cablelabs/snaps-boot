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

logger = logging.getLogger('pxe_utils')


def static_ip_configure(config):
    logger.info("Attempting to configure the nodes' NICs")

    prov_dict = config.get('PROVISION')
    proxy_dict = prov_dict.get('PROXY')
    static_dict = prov_dict.get('STATIC')

    hosts = static_dict.get('host')
    valid = __validate_static_config(static_dict)
    if valid is False:
        logger.info(
            "Configuration error please define IP for all the interface types")
        exit(1)
    http_proxy = proxy_dict.get('http_proxy')
    https_proxy = proxy_dict.get('https_proxy')
    # iplist = []

    # for this_host in host:
    #     target = this_host.get('access_ip')
    #     iplist.append(target)
    for host in hosts:
        interfaces = host.get('interfaces')
        backup_var = "Y"
        playbook_path_bak = pkg_resources.resource_filename(
            'snaps_boot.ansible_p.commission', 'interfaceBak.yaml')
        pb_user = 'root'
        pb_vars = {'bak': backup_var}
        ip = host.get('access_ip')

        logger.info('Executing %s on host %s with user %s and vars %s',
                    playbook_path_bak, ip, pb_user, pb_vars)
        ansible_utils.apply_playbook(
            playbook_path_bak, [ip], host_user=pb_user,
            variables=pb_vars)

        playbook_path = pkg_resources.resource_filename(
            'snaps_boot.ansible_p.commission', 'setIPConfig.yaml')
        for interface in interfaces:
            pb_vars = {
                'address': interface.get('address'),
                'gateway': interface.get('gateway'),
                'netmask': interface.get('netmask'),
                'iface': interface.get('iface'),
                'http_proxy': http_proxy,
                'https_proxy': https_proxy,
                'type': interface.get('type'),
                'dns': interface.get('dns'),
                'dn': interface.get('dn')
            }
            ansible_utils.apply_playbook(
                playbook_path, [ip], host_user=pb_user,
                variables=pb_vars)


def static_ip_cleanup(config):
    prov_dict = config.get('PROVISION')
    static_dict = prov_dict.get('STATIC')

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


def set_isol_cpus(config):
    """
    to   set isolate cpu  in /etc/default/grub file
    """
    logger.info("setIsolCpus function")
    prov_dict = config.get('PROVISION')
    cpu_core_dict = prov_dict.get('CPUCORE')

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


def del_isol_cpus(config):
    """
    to set isolate cpu  in /etc/default/grub file
    """
    logger.info("setIsolCpus function")
    prov_dict = config.get('PROVISION')
    cpu_core_dict = prov_dict.get('CPUCORE')

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
