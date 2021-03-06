# Copyright 2018 ARICENT HOLDINGS LUXEMBOURG SARL and Cable Television
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

import logging

from pyghmi.ipmi.command import Command
from pyghmi.exceptions import IpmiException

logger = logging.getLogger('snaps_boot_ipmi_utils')
# logger.setLevel(logging.DEBUG)


def reboot_pxe(boot_conf):
    """
    Sets the boot order to 'pxe' then reboots all configured nodes
    :param boot_conf: the boot configuration
    """
    __reboot_all(boot_conf, 'network')


def reboot_disk(boot_conf):
    """
    Sets the boot order to 'disk' then reboots all configured nodes
    :param boot_conf: the boot configuration
    """
    __reboot_all(boot_conf, 'hd')


def __reboot_all(boot_conf, boot_order):
    creds = get_ipmi_creds(boot_conf)
    for ip, user, password in creds:
        try:
            command = Command(ip, user, password)
            __set_boot_order(command, boot_order)
            __reboot(command)
            logger.info('Successfully rebooted server with BMC IP: %s', ip)
        except IpmiException as e:
            # print the error message and server bmc information
            # will continue to reboot the rest of servers
            logger.error(
                'Failed to reboot server with BMC IP: %s, user: %s, error: %s',
                ip, user, e)
            logger.debug('BMC password: %s', password)


def get_ipmi_creds(boot_conf):
    """
    Returns a list of tuple 3 objects containing the IPMI credentials where
    index 0 is the IP, 1 is the username, and 2 is the password
    :param boot_conf: the boot configuration
    """
    out = list()
    hosts_dict = boot_conf['PROVISION']['BMC']['host']
    for host_dict in hosts_dict:
        out.append((host_dict['ip'], host_dict['user'], host_dict['password']))
    return out


def __set_boot_order(command, order):
    command.set_bootdev(order)


def __reboot(command):
    command.set_power('boot')
