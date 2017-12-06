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

#This script is responsible for calling all the playbooks responsible for deploying openstack services

import logging

from collections import namedtuple

import os
#import paramiko
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
import ansible.constants
#from ansible.executor.playbook_executor import PlaybookExecutor
#from ansible.parsing.dataloader import DataLoader
#from ansible.vars import VariableManager
#from ansible.inventory import Inventory
#import ansible.constants

__author__ = 'parwinder'

logger = logging.getLogger('ansible_playbook_operations')
def __launch_ansible_playbook(list_ip, playbook, extra_variable=None, proxy_setting=None):
    """
    Applies an Ansible playbook
    :param playbook: the playboo to be applied
    """
    print extra_variable
    if not os.path.isfile(playbook):
        raise Exception('Requested playbook is not found - ' + playbook)

    if not playbook:
         logger.warn('Unable to find playbook - ' + playbook)

    #ansible.constants.HOST_KEY_CHECKING = False

    variable_manager = VariableManager()
    #variable_manager.extra_vars =  None
    #if extra_variable is not None


    if extra_variable is not None:
     variable_manager.extra_vars = extra_variable
     logger.info(extra_variable)
    else:
     logger.info('NO EXTRA VARS')
    loader = DataLoader()
    inventory = Inventory(loader=loader, variable_manager=variable_manager, host_list=list_ip)
    variable_manager.set_inventory(inventory)
    #print hosts.name
    ssh_extra_args = None
    if proxy_setting and proxy_setting.ssh_proxy_cmd:
        ssh_extra_args = '-o ProxyCommand=\'' + proxy_setting.ssh_proxy_cmd + '\''

    options = namedtuple('Options', ['listtags', 'listtasks', 'listhosts', 'syntax', 'connection', 'module_path',
                                     'forks', 'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args',
                                     'become', 'become_method', 'become_user', 'verbosity', 'check', 'sftp_extra_args', 'scp_extra_args'])

    ansible_opts = options(listtags=None, listtasks=None, listhosts=None, syntax=False, connection='ssh',
                           module_path=None, forks=100, remote_user=None, private_key_file=None,
                           ssh_common_args=None, ssh_extra_args=None, become=True, become_method='sudo',
                           become_user=None, verbosity=11111, check=False,sftp_extra_args=None, scp_extra_args=None)

    logger.debug('Setting up Ansible Playbook Executor for playbook - ' + playbook)
    executor = PlaybookExecutor(
        playbooks=[playbook],
        inventory=inventory,
        variable_manager=variable_manager,
        loader=loader,
        options=ansible_opts,
        passwords=None)

    logger.debug('Executing Ansible Playbook - ' + playbook)
    ret= executor.run()
    return ret
