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
import logging

import pkg_resources
from drp_python.model_layer.subnet_model import SubnetModel
from drp_python.subnet import Subnet
# from drp_python.model_layer.reservation_model import ReservationModel
# from drp_python.reservation import Reservation
from drp_python.model_layer.machine_model import MachineModel
from drp_python.machine import Machine
from snaps_common.ansible_snaps import ansible_utils

logger = logging.getLogger('rebar_utils')


def setup_dhcp_service(rebar_session, boot_conf):
    """
    Creates a DHCP service
    :param rebar_session: the Digital Rebar session object
    :param boot_conf: the configuration
    :raises Exceptions
    """
    __setup_drp()
    __create_images()
    __create_workflows()
    __create_content_pack()
    __create_subnet(rebar_session, boot_conf)
    __create_reservations(rebar_session, boot_conf)
    __create_machines(rebar_session, boot_conf)


def cleanup_dhcp_service(rebar_session, boot_conf):
    """
    Creates a DHCP service
    :param rebar_session: the Digital Rebar session object
    :param boot_conf: the configuration
    :raises Exceptions
    """
    logger.info('Removing Digital Rebar objects for DHCP/PXE booting')
    __delete_machines(rebar_session, boot_conf)
    __delete_reservations(rebar_session, boot_conf)
    __delete_subnet(rebar_session, boot_conf)
    __delete_content_pack()
    __teardown_drp()


def __setup_drp():
    """
    Installs DRP and creates required objects
    :raises Exceptions
    """
    logger.info('Setting up Digital Rebar objects for DHCP/PXE booting')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_setup.yaml')
    ansible_utils.apply_playbook(playbook_path)


def __teardown_drp():
    """
    Installs DRP and creates required objects
    :raises Exceptions
    """
    logger.info('Setting up Digital Rebar objects for DHCP/PXE booting')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_teardown.yaml')
    ansible_utils.apply_playbook(playbook_path)


def __create_images():
    """
    Creates a Digital Rebar image objects
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Creating content pack')
    logger.info('Setting up Digital Rebar objects for DHCP/PXE booting')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_workflows_create.yaml')
    ansible_utils.apply_playbook(playbook_path)


def __create_workflows():
    """
    Creates a Digital Rebar workflow objects
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Creating content pack')
    logger.info('Setting up Digital Rebar objects for DHCP/PXE booting')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_workflows_create.yaml')
    ansible_utils.apply_playbook(playbook_path)


def __create_content_pack():
    """
    Creates a Digital Rebar subnet object
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Creating content pack')
    pack_dir = pkg_resources.resource_filename('snaps_boot', 'drp_content')

    logger.info('Setting up Digital Rebar objects for DHCP/PXE booting')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_content_pack_create.yaml')
    ansible_utils.apply_playbook(
        playbook_path, variables={'content_dir': pack_dir})


def __delete_content_pack():
    """
    Deletes a Digital Rebar subnet object
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Deleting content pack')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_content_pack_destroy.yaml')
    ansible_utils.apply_playbook(playbook_path)


def __create_subnet(rebar_session, boot_conf):
    """
    Creates a Digital Rebar subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    subnet = __instantiate_drp_subnet(rebar_session, boot_conf)
    logger.info('Attempting to create DRP subnet')
    subnet.create()


def __delete_subnet(rebar_session, boot_conf):
    """
    Deletes a Digital Rebar subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    subnet = __instantiate_drp_subnet(rebar_session, boot_conf)
    logger.info('Attempting to delete DRP subnet')
    subnet.delete()


def __instantiate_drp_subnet(rebar_session, boot_conf):
    """
    Instantiates a drp_python.subnet.Subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :return: a Subnet object
    """
    # TODO/FIXME - Why are there multiple subnets configured
    subnet_conf = boot_conf['PROVISION']['DHCP']['subnet'][0]
    # TODO/FIXME - Create function to return a SubnetModel so we can support
    # TODO/FIXME - different types of configurations
    logger.info('Instantiating DRP subnet object with values %s', subnet_conf)
    drp_subnet_conf = SubnetModel(**subnet_conf)
    return Subnet(rebar_session, drp_subnet_conf)


def __create_reservations(rebar_session, boot_conf):
    """
    Creates all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    reservations = __instantiate_drp_reservations(rebar_session, boot_conf)
    logger.info('Attempting to create DRP reservations')
    for reservation in reservations:
        logger.debug('Attempting to create DRP reservation %s', reservation)
        reservation.create()


def __delete_reservations(rebar_session, boot_conf):
    """
    Deletes all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    reservations = __instantiate_drp_reservations(rebar_session, boot_conf)
    logger.info('Attempting to delete DRP reservations')
    for reservation in reservations:
        logger.debug('Attempting to delete DRP reservation %s', reservation)
        reservation.delete()


def __instantiate_drp_reservations(rebar_session, boot_conf):
    """
    Instantiates and returns the configured drp_python.reservation.Reservation
    objects
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :return: a list of Reservation objects
    """
    out = list()
    # TODO/FIXME - Why are there multiple subnets configured
    subnet_conf = boot_conf['PROVISION']['DHCP']['subnet'][0]

    bind_hosts = subnet_conf['bind_host']
    # for bind_host in bind_hosts:
    #     drp_res_conf = ReservationModel(**bind_host)
    #     out.append(Reservation(rebar_session, drp_res_conf))

    return out


def __create_machines(rebar_session, boot_conf):
    """
    Creates all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    machines = __instantiate_drp_machines(rebar_session, boot_conf)
    logger.info('Attempting to create DRP machines')
    for machine in machines:
        logger.debug('Attempting to create DRP machine %s', machine)
        machine.create()
        logger.info('Created machine %s', machine)


def __delete_machines(rebar_session, boot_conf):
    """
    Deletes all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    machines = __instantiate_drp_machines(rebar_session, boot_conf)
    logger.info('Attempting to create DRP machines')
    for machine in machines:
        logger.debug('Attempting to delete DRP machine %s', machine)
        machine.delete()


def __instantiate_drp_machines(rebar_session, boot_conf):
    """
    Instantiates and returns the configured drp_python.machine.Machine objects
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :return: a list of Machine objects
    """
    out = list()
    prov_conf = boot_conf['PROVISION']
    host_confs = prov_conf['STATIC']['host']
    tftp_conf = prov_conf['TFTP']
    dhcp_conf = prov_conf['DHCP']
    # TODO/FIXME - Why are there multiple subnets configured
    subnet_conf = dhcp_conf['subnet'][0]
    bind_hosts_confs = subnet_conf['bind_host']
    pxe_confs = tftp_conf.get('pxe_server_configuration')
    if pxe_confs:
        if isinstance(pxe_confs, list):
            # TODO/FIXME - Determine how to deal with multiple PXE configs???
            pxe_conf = pxe_confs[0]
        else:
            pxe_conf = pxe_confs
    else:
        raise Exception('Could not locate the PXE configuration for parsing')

    for host_conf in host_confs:
        drp_mach_conf = __get_drb_machine_config(
            host_conf, pxe_conf, bind_hosts_confs)
        out.append(Machine(rebar_session, drp_mach_conf))

    return out


def __get_drb_machine_config(host_conf, pxe_conf, bind_host_confs):

    operating_sys = None
    for key, the_conf in pxe_conf.items():
        operating_sys = the_conf.get('os')

    mac = None
    for bind_host_conf in bind_host_confs:
        if bind_host_conf['ip'] == host_conf['access_ip']:
            mac = bind_host_conf['mac']

    if not operating_sys or not mac:
        raise Exception('Cannot find the OS MAC configuration')

    # TODO/FIXME - os and workflow must be hardcoded now
    drp_mach_dict = {
        'ip': host_conf['access_ip'],
        'mac': mac,
        'name': host_conf['name'],
        'os': 'ubuntu-16.04.5-server-amd64.iso',
        'type': 'snaps-boot',
        'workflow': 'snaps-ubuntu-16.04'
    }

    logger.info('Instantiating a MachineModel object with %s', drp_mach_dict)

    return MachineModel(**drp_mach_dict)
