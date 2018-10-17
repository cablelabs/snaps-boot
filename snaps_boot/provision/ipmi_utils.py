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
from pyghmi.ipmi.command import Command


def reboot_pxe(boot_conf):
    """
    Sets the boot order to 'disk' then reboots
    :param boot_conf: the boot configuration
    """
    ip, user, password = __get_ipmi_creds(boot_conf)
    command = Command(ip, user, password)
    __set_boot_order(command, 'hd')
    __reboot(command)


def reboot_disk(boot_conf):
    """
    Sets the boot order to 'pxe' then reboots
    :param boot_conf: the boot configuration
    """
    ip, user, password = __get_ipmi_creds(boot_conf)
    command = Command(ip, user, password)
    __set_boot_order(command, 'network')
    __reboot(command)


def __get_ipmi_creds(boot_conf):
    """
    Returns a tuple 3 containing the IPMI credentials where index 0 is the IP,
    1 is the username, and 2 is the password
    :param boot_conf: the boot configuration
    """
    return boot_conf['ip'], boot_conf['user'], boot_conf['password']


def __set_boot_order(command, order):
    command.set_bootdev(order)


def __reboot(command):
    power = command.get_power()
    if 'on' == power['powerstate']:
        command.set_power('off')

    power = command.get_power()
    if 'on' == power['powerstate']:
        raise Exception('Chassis never powered down')
    command.set_power('on')
