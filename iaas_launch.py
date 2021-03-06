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

# This script is responsible for deploying Aricent_Iaas environments and
# Openstack Services
import argparse
import getpass
import logging

import os
import sys

from drp_python.network_layer.http_session import HttpSession
from snaps_common.file import file_utils
from snaps_boot.provision import pxe_utils, rebar_utils, ipmi_utils

logger = logging.getLogger('iaas_launch')

ARG_NOT_SET = "argument not set"


def __run(arguments):
    """
     This will launch the provisioning of Bare metat & IaaS.
     There is pxe based configuration defined to provision the bare metal.
     For IaaS provisioning different deployment models are supported.
     Relevant conf files related to PXE based Hw provisioning & Openstack based
     IaaS must be present in ./conf folder.
     :param arguments: This expects command line options to be entered by user
                       for relavant operations.
     :return: To the OS
    """

    log_level = logging.INFO
    if arguments.log_level != 'INFO':
        log_level = logging.DEBUG
    logging.basicConfig(stream=sys.stdout, level=log_level)

    logger.info('Launching Operation Starts ........')

    user = getpass.getuser()
    logger.info('Running as user %s', user)

    config_filepath = os.path.expanduser(arguments.config)
    logger.info('Reading configuration file [%s]', config_filepath)
    config = file_utils.read_yaml(config_filepath)

    prv_config = config.get('PROVISION')
    if not prv_config:
        raise Exception('Missing top-level config member PROVISION')
    logger.debug('PROVISION configuration %s', prv_config)

    # TODO/FIXME - Hardcoding of user/pass should be configurable
    drp_config = prv_config.get('digitalRebar')
    if drp_config:
        logger.info('Rebar configuration %s', drp_config)
        user = drp_config.get('user', 'rocketskates')
        password = drp_config.get('password', 'r0cketsk8ts')
    else:
        user = 'rocketskates'
        password = 'r0cketsk8ts'

    # TODO/FIXME - DRP host and port should be configurable
    rebar_session = HttpSession(
        'https://localhost:8092', user, password)

    if arguments.hardware is not ARG_NOT_SET:
        rebar_utils.install_config_drp(rebar_session, config)

    if arguments.provisionClean is not ARG_NOT_SET:
        rebar_utils.cleanup_drp(rebar_session, config)

    if arguments.staticIPCleanup is not ARG_NOT_SET:
        # Do we really need to support this function?
        pxe_utils.static_ip_cleanup(config)

    if arguments.staticIPConfigure is not ARG_NOT_SET:
        # Is this something that we should do with cloud-init or other means
        # immediately after the OS is laid down?
        pxe_utils.static_ip_configure(config)

    if arguments.boot is not ARG_NOT_SET:
        ipmi_utils.reboot_pxe(config)

    if arguments.bootd is not ARG_NOT_SET:
        # This power cycles the nodes
        ipmi_utils.reboot_disk(config)
    if arguments.setIsolCpus is not ARG_NOT_SET:
        # This operation is unclear
        pxe_utils.set_isol_cpus(config)
    if arguments.delIsolCpus is not ARG_NOT_SET:
        # This operation is unclear
        pxe_utils.del_isol_cpus(config)
    logger.info('Completed operation successfully')


if __name__ == '__main__':
    # To ensure any files referenced via a relative path will begin from the
    # diectory in which this file resides
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-p',
        '--provision',
        dest='hardware',
        nargs='?',
        default=ARG_NOT_SET,
        help='When used, setting up of pxe server and '
        'provisioning of PXE clients will be started')
    parser.add_argument(
        '-f',
        '--file',
        dest='config',
        required=True,
        help='The configuration file in YAML format'
        ' - REQUIRED',
        metavar="FILE")
    parser.add_argument(
        '-l',
        '--log-level',
        dest='log_level',
        default='INFO',
        help='Logging Level (INFO|DEBUG)')
    parser.add_argument(
        '-b',
        '--boot',
        dest='boot',
        nargs='?',
        default=ARG_NOT_SET,
        help='When used, to boot the system via pxe')
    parser.add_argument(
        '-bd',
        '--bootd',
        dest='bootd',
        nargs='?',
        default=ARG_NOT_SET,
        # TODO/FIXME - Does this operation really do anything differently
        # CI just calls -b in other contexts and those machines are booting
        # from the internal storage
        help='When used, to boot the system via hdd')
    parser.add_argument(
        '-pc',
        '--provisionClean',
        dest='provisionClean',
        nargs='?',
        default=ARG_NOT_SET,
        help='Cleanup boot environment')
    parser.add_argument(
        '-s',
        '--staticIPConfigure',
        dest='staticIPConfigure',
        nargs='?',
        default=ARG_NOT_SET,
        help='Configure static IPs on boot nodes')
    parser.add_argument(
        '-sc',
        '--staticIPCleanup',
        dest='staticIPCleanup',
        nargs='?',
        default=ARG_NOT_SET,
        help='Cleans up static IPs on nodes')
    parser.add_argument(
        '-i',
        '--setIsolCpus',
        dest='setIsolCpus',
        nargs='?',
        default=ARG_NOT_SET,
        # TODO/FIXME - Description is incorrect
        help='When used, the pxe server environment will be removed')
    parser.add_argument(
        '-ic',
        '--cleanIsolCpus',
        dest='delIsolCpus',
        nargs='?',
        default=ARG_NOT_SET,
        # TODO/FIXME - Description is incorrect
        help='When used, the pxe server environment will be removed')
    args = parser.parse_args()

    if (args.hardware is ARG_NOT_SET and args.boot is ARG_NOT_SET and
            args.bootd is ARG_NOT_SET and
            args.provisionClean is ARG_NOT_SET and
            args.setIsolCpus is ARG_NOT_SET and
            args.delIsolCpus is ARG_NOT_SET and
            args.staticIPConfigure is ARG_NOT_SET and
            args.staticIPCleanup is ARG_NOT_SET):
        print 'Must enter either -p for provision hardware or -pc for clean ' \
              'provision hardware or -b for boot or -i for isolate cpu ' \
              'provision or -bd for boot from disk'
        exit(1)
    if args.hardware is ARG_NOT_SET and args.config is ARG_NOT_SET:
        print 'Cannot start any deploy iaas operation without -p/--provision' \
              ' and -f/--file'
        exit(1)

    __run(args)
