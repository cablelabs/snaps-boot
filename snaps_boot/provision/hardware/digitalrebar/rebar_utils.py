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
import os

import pkg_resources
from drp_python.model_layer.subnet_model import SubnetModel
from drp_python.subnet import Subnet
# from drp_python.model_layer.reservation_model import ReservationModel
# from drp_python.reservation import Reservation
# from drp_python.model_layer.machine_model import MachineModel
# from drp_python.machine import Machine

logger = logging.getLogger('rebar_utils')


def setup_dhcp_service(rebar_session, boot_conf):
    """
    Creates a DHCP service
    :param rebar_session: the Digital Rebar session object
    :param boot_conf: the configuration
    :raises Exceptions
    """
    logger.info('Setting up Digital Rebar objects for DHCP/PXE booting')
    __create_content_pack(rebar_session, boot_conf)
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
    __delete_content_pack(rebar_session, boot_conf)


def __create_content_pack(rebar_session, boot_conf):
    """
    Creates a Digital Rebar subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Creating content pack')
    pack_dir = pkg_resources.resource_filename('snaps_boot', 'drp_content')
    os.chdir(pack_dir)

    gen_cmd = 'drpcli contents bundle snaps-content.yaml'
    retval = os.system(gen_cmd)
    if retval != 0:
        raise Exception('Command failed [%s]', gen_cmd)

    upload_cmd = 'drpcli contents upload snaps-content.yaml'
    retval = os.system(upload_cmd)
    if retval != 0:
        raise Exception('Command failed [%s]', upload_cmd)


def __delete_content_pack(rebar_session, boot_conf):
    """
    Deletes a Digital Rebar subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Deleting content pack')
    pack_dir = pkg_resources.resource_filename('snaps_boot', 'drp_content')
    os.chdir(pack_dir)

    delete_cmd = 'drpcli contents destroy snaps-content'
    retval = os.system(delete_cmd)
    if retval != 0:
        logger.warn('Command failed [%s]', delete_cmd)


def __create_subnet(rebar_session, boot_conf):
    """
    Creates a Digital Rebar subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    subnet = __instantiate_drp_subnet(rebar_session, boot_conf)
    subnet.create()


def __delete_subnet(rebar_session, boot_conf):
    """
    Deletes a Digital Rebar subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    subnet = __instantiate_drp_subnet(rebar_session, boot_conf)
    subnet.delete()


def __instantiate_drp_subnet(rebar_session, boot_conf):
    """
    Instantiates a drp_python.subnet.Subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :return: a Subnet object
    """
    subnet_conf = boot_conf['PROVISION']['DHCP']['subnet'][0]
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
    for reservation in reservations:
        reservation.create()


def __delete_reservations(rebar_session, boot_conf):
    """
    Deletes all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    reservations = __instantiate_drp_reservations(rebar_session, boot_conf)
    for reservation in reservations:
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
    for machine in machines:
        machine.create()


def __delete_machines(rebar_session, boot_conf):
    """
    Deletes all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    machines = __instantiate_drp_machines(rebar_session, boot_conf)
    for machine in machines:
        machine.delete()


def __instantiate_drp_machines(rebar_session, boot_conf):
    """
    Instantiates and returns the configured drp_python.machine.Machine objects
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :return: a list of Machine objects
    """
    out = list()
    host_confs = boot_conf['PROVISION']['STATIC']['host']
    # for host_conf in host_confs:
    #     drp_mach_conf = MachineModel(**host_conf)
    #     out.append(Machine(rebar_session, drp_mach_conf))

    return out
