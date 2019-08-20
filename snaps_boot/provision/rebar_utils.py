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
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from drp_python.model_layer.params_model import ParamsModel
from drp_python.model_layer.subnet_model import SubnetModel
from drp_python.subnet import Subnet
from drp_python.model_layer.reservation_model import ReservationModel
from drp_python.reservation import Reservation
from drp_python.model_layer.machine_model import MachineModel
from drp_python.machine import Machine
from snaps_common.ansible_snaps import ansible_utils

logger = logging.getLogger('rebar_utils')

LOCAL_PRIV_KEY_FILE = os.path.expanduser('~/.ssh/id_rsa')
LOCAL_PUB_KEY_FILE = os.path.expanduser('~/.ssh/id_rsa.pub')


def install_config_drp(rebar_session, boot_conf):
    """
    Creates a DHCP service
    :param rebar_session: the Digital Rebar session object
    :param boot_conf: the configuration
    :raises Exceptions
    """
    logger.info('Setting up Digital Rebar service and objects')
    __setup_proxy_server(boot_conf)
    __setup_drp(boot_conf)
    __create_images(boot_conf)
    __create_subnet(rebar_session, boot_conf)
    __create_workflows()
    __upload_postscript(boot_conf)
    __create_reservations(rebar_session, boot_conf)
    __create_content_pack()
    __create_machines(rebar_session, boot_conf)


def __setup_proxy_server(boot_conf):
    logger.info('Setting up ng-cacher-proxy')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'setup_proxy_server.yaml')
    ansible_utils.apply_playbook(playbook_path, variables={
        'http_proxy': boot_conf['PROVISION']['PROXY']['http_proxy']})


def cleanup_drp(rebar_session, boot_conf):
    """
    Creates a DHCP service
    :param rebar_session: the Digital Rebar session object
    :param boot_conf: the configuration
    :raises Exceptions
    """
    logger.info('Cleaning up and disabling Digital Rebar')
    __delete_machines(rebar_session, boot_conf)
    __delete_content_pack()
    __delete_reservations(rebar_session, boot_conf)
    __delete_subnet(rebar_session, boot_conf)
    __delete_workflows()
    __delete_images()
    __teardown_drp()


def __setup_drp(boot_conf):
    """
    Installs DRP and creates required objects
    :raises Exceptions
    """
    logger.info('Setting up Digital Rebar objects for DHCP/PXE booting')
    prov_conf = boot_conf['PROVISION']
    http_proxy = prov_conf['PROXY']['http_proxy']
    https_proxy = prov_conf['PROXY']['https_proxy']
    drp_version = prov_conf['digitalRebar'].get('version', 'stable')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_setup.yaml')
    ansible_utils.apply_playbook(playbook_path, variables={
        'server_ip': boot_conf['PROVISION']['PXE']['server_ip'],
        'http_proxy': http_proxy, 'https_proxy': https_proxy,
        'drp_version': drp_version})


def __teardown_drp():
    """
    Installs DRP and creates required objects
    :raises Exceptions
    """
    try:
        logger.info('Stopping and disabling Digital Rebar')
        playbook_path = pkg_resources.resource_filename(
            'snaps_boot.ansible_p.setup', 'drp_teardown.yaml')
        ansible_utils.apply_playbook(playbook_path)
    except Exception as e:
        logger.warn('Unable to teardown DRP - [%s]', e)


def __create_images(boot_conf):
    """
    Creates a Digital Rebar image objects
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Setting up Digital Rebar images')
    prov_conf = boot_conf['PROVISION']
    http_proxy = prov_conf['PROXY']['http_proxy']
    https_proxy = prov_conf['PROXY']['https_proxy']
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_images_create.yaml')
    ansible_utils.apply_playbook(playbook_path, variables={
        'http_proxy': http_proxy, 'https_proxy': https_proxy})


def __delete_images():
    """
    Creates a Digital Rebar image objects
    :raises Exceptions
    """
    try:
        # TODO/FIXME - find appropriate API to perform these tasks
        logger.info('Deleting Digital Rebar images')
        playbook_path = pkg_resources.resource_filename(
            'snaps_boot.ansible_p.setup', 'drp_images_destroy.yaml')
        ansible_utils.apply_playbook(playbook_path)
    except Exception as e:
        logger.warn('Unable to delete all images - [%s]', e)


def __create_workflows():
    """
    Creates a Digital Rebar workflow objects
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Setting up Digital Rebar workflows')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_workflows_create.yaml')
    ansible_utils.apply_playbook(playbook_path)


def __delete_workflows():
    """
    Creates a Digital Rebar workflow objects
    :raises Exceptions
    """
    try:
        # TODO/FIXME - find appropriate API to perform these tasks
        logger.info('Deleting up Digital Rebar workflows')
        playbook_path = pkg_resources.resource_filename(
            'snaps_boot.ansible_p.setup', 'drp_workflows_destroy.yaml')
        ansible_utils.apply_playbook(playbook_path)
    except Exception as e:
        logger.warn('Unable to delete workflows - [%s]', e)


def __upload_postscript(boot_conf):
    logger.info('Uploading post script')
    prov_conf = boot_conf['PROVISION']
    pxe_confs = prov_conf['TFTP']['pxe_server_configuration']
    post_script_location = None
    for value in pxe_confs.values():
        # post_script_location is optional, so use get() to avoid KeyError
        post_script_location = value.get('post_script_location')
        break

    if post_script_location:
        playbook_path = pkg_resources.resource_filename(
            'snaps_boot.ansible_p.setup', 'upload_postscript.yaml')
        ansible_utils.apply_playbook(playbook_path, variables={
            'post_script_file': post_script_location})


def __create_content_pack():
    """
    Creates a Digital Rebar subnet object
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Creating Digital Rebar content pack')
    pack_dir = pkg_resources.resource_filename('snaps_boot', 'drp_content')

    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_content_pack_create.yaml')
    ansible_utils.apply_playbook(playbook_path, variables={
        'content_dir': pack_dir, 'content_pkg': 'drp_content'})


def __delete_content_pack():
    """
    Deletes a Digital Rebar subnet object
    :raises Exceptions
    """
    # TODO/FIXME - find appropriate API to perform these tasks
    logger.info('Deleting content pack')
    playbook_path = pkg_resources.resource_filename(
        'snaps_boot.ansible_p.setup', 'drp_content_pack_destroy.yaml')

    try:
        ansible_utils.apply_playbook(playbook_path)
    except Exception as e:
        logger.warn('Unexpected error deleting content bundle - %s', e)


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
    try:
        subnet = __instantiate_drp_subnet(rebar_session, boot_conf)
        logger.info('Attempting to delete DRP subnet')
        subnet.delete()
    except Exception as e:
        logger.warn('Unable to delete subnet - [%s]', e)


def __instantiate_drp_subnet(rebar_session, boot_conf):
    """
    Instantiates a drp_python.subnet.Subnet object
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :return: a Subnet object
    """
    # TODO/FIXME - Why are there multiple subnets configured
    subnet_conf = boot_conf['PROVISION']['DHCP']['subnet'][0]
    # Add the PXE server IP as next server for DHCP
    # (required for shared build server to work)
    subnet_conf['next_server'] = boot_conf['PROVISION']['PXE']['server_ip']
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

    logger.info('Completed creating %s reservations', len(reservations))


def __delete_reservations(rebar_session, boot_conf):
    """
    Deletes all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    try:
        reservations = __instantiate_drp_reservations(rebar_session, boot_conf)
        logger.info('Attempting to delete DRP reservations')
        for reservation in reservations:
            logger.debug('Attempting to delete DRP reservation %s',
                         reservation)
            reservation.delete()
    except Exception as e:
        logger.warn('Unable to delete all reservations - [%s]', e)


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
    prov_confs = boot_conf['PROVISION']
    subnet_conf = prov_confs['DHCP']['subnet'][0]

    bind_hosts = subnet_conf['bind_host']
    for bind_host in bind_hosts:
        res_conf = {
            'ip': bind_host['ip'],
            'mac': bind_host['mac'],
            'name': bind_host['mac'],
            'type': 'admin',
        }
        logger.info('Creating DRP reservation %s', res_conf)
        drp_res_conf = ReservationModel(**res_conf)
        res = Reservation(rebar_session, drp_res_conf)
        out.append(res)

    return out


def __get_pub_key():
    """
    Ensures that the build server has SSH keys to inject into nodes
    :return: the public key value
    """
    logger.info('Generate SSH keys')
    public_key, private_key = __get_existing_keys()

    if public_key and private_key:
        logger.info('Existing pubic key [%s]', public_key)
        return public_key
    else:
        return __create_keys()[0]


def __create_keys(key_size=2048):
    """
    Generates public and private keys
    :param key_size: the number of bytes for the key size
    :return: tuple 3 where 0 is the public key, 1 is the private key, and
             2 is a boolean where True means the key was created and False
             means it already existed
    """
    public_key, private_key = __get_existing_keys()

    if public_key and private_key:
        logger.info('Existing pubic key [%s]', public_key)
        return public_key, private_key, False
    else:
        logger.info('Generate keys')
        keys = rsa.generate_private_key(
            backend=default_backend(), public_exponent=65537,
            key_size=key_size)

        public_key = keys.public_key().public_bytes(
            serialization.Encoding.OpenSSH,
            serialization.PublicFormat.OpenSSH)
        private_key = keys.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption())

        logger.debug('Generated public key - %s', public_key)
        logger.debug('Generated private key - %s', private_key)

        __store_current_key(public_key, private_key)

        return public_key, private_key, True


def __get_existing_keys():
    logger.info('Checking if file [%s] exists', LOCAL_PUB_KEY_FILE)
    logger.info('Checking if file [%s] exists', LOCAL_PRIV_KEY_FILE)

    if (not os.path.isfile(LOCAL_PUB_KEY_FILE)
            or not os.path.isfile(LOCAL_PRIV_KEY_FILE)):
        logger.warn('Keys not found [%s] & [%s]',
                    LOCAL_PUB_KEY_FILE, LOCAL_PRIV_KEY_FILE)
        return None, None

    with open(LOCAL_PUB_KEY_FILE, 'r') as ssh_pub_key_file:
        pub_contents = ssh_pub_key_file.readlines()
    with open(LOCAL_PRIV_KEY_FILE, 'r') as ssh_priv_key_file:
        priv_contents = ssh_priv_key_file.readlines()

    return pub_contents[0], priv_contents[0]


def __store_current_key(pubic_key, private_key):
    logger.info('Writing keys to [%s] & [%s]',
                LOCAL_PUB_KEY_FILE, LOCAL_PRIV_KEY_FILE)
    with open(LOCAL_PUB_KEY_FILE, 'wb') as pub_key_file:
        pub_key_file.write(pubic_key)
        os.chmod(LOCAL_PUB_KEY_FILE, 0600)
    with open(LOCAL_PRIV_KEY_FILE, 'wb') as priv_key_file:
        priv_key_file.write(private_key)
        os.chmod(LOCAL_PRIV_KEY_FILE, 0600)


def __create_machines(rebar_session, boot_conf):
    """
    Creates all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    public_key = __get_pub_key()

    machines = __instantiate_drp_machines(rebar_session, boot_conf)
    logger.info('Attempting to create %s DRP machines', len(machines))
    for machine in machines:
        logger.debug('Attempting to create DRP machine %s', machine)
        machine.create()
        # TODO - Make keys configurable for different users
        __add_machine_params(boot_conf, machine, public_key)
        logger.info('Created machine %s', machine)


def __add_machine_params(boot_conf, machine, public_key):
    """
    Adds parameters to machine object
    :param boot_conf: the boot configuration
    :raises Exception
    """
    logger.info('Adding parameters to machine %s', machine)
    params = __create_machine_params(boot_conf, machine, public_key)
    for param in params:
        logger.info('Adding param %s', param)
        machine.add_param_values(param)


def __create_machine_params(boot_conf, machine, public_key):
    """
    Instantiates all drp-python ParamsConfigModel objects
    :param boot_conf: the boot configuration
    :return: list of all config models
    """
    out = list()
    prov_conf = boot_conf['PROVISION']
    pxe_confs = prov_conf['TFTP']['pxe_server_configuration']
    install_disk = None
    user_password = None
    user = None
    fullname = None
    kernel_choice = None
    post_script_location = None
    for value in pxe_confs.values():
        user_password = value['password']
        user = value['user']
        fullname = value['fullname']
        install_disk = value['boot_disk']
        # kernel_choice is optional, so use get() to avoid KeyError
        kernel_choice = value.get('kernel_choice')
        # post_script_location is optional, so use get() to avoid KeyError
        post_script_location = value.get('post_script_location')
        break

    if not install_disk or not user_password or not user or not fullname:
        raise Exception('Cannot set expected seed values')

    out.append(ParamsModel(name='seed/user-password', value=user_password))
    out.append(ParamsModel(name='seed/username', value=user))
    out.append(ParamsModel(name='seed/user-fullname', value=fullname))
    out.append(ParamsModel(name='operating-system-disk', value=install_disk))
    if kernel_choice:
        out.append(
            ParamsModel(name='seed/kernel-choice', value=kernel_choice))

    root_password = prov_conf['PXE']['password']
    server_ip = prov_conf['PXE']['server_ip']
    out.append(ParamsModel(name='seed/root-password', value=root_password))
    out.append(ParamsModel(name='seed/server-ip', value=server_ip))

    host_confs = boot_conf['PROVISION']['STATIC']['host']
    for host_conf in host_confs:
        if host_conf['access_ip'] == machine.get().ip:
            post_script_url = host_conf.get('post_script_url')
            if post_script_url:
                # set the param with user provided post_script_url
                out.append(ParamsModel(name='post/script-url',
                                       value=post_script_url))
            elif post_script_location:
                # set the param with the global post script url
                out.append(
                    ParamsModel(name='post/script-url',
                                value='http://' + server_ip +
                                      ':8091/files/post_script'))
            break

    machine_proxy = prov_conf.get('NODE_PROXY')
    http_proxy = None
    https_proxy = None
    if machine_proxy:
        http_proxy = machine_proxy['http_proxy']
        https_proxy = machine_proxy['https_proxy']
    apt_proxy = prov_conf['PROXY']['ngcacher_proxy']

    if http_proxy:
        out.append(ParamsModel(name='post/http-proxy', value=http_proxy))
    if https_proxy:
        out.append(ParamsModel(name='post/https-proxy', value=https_proxy))
    if apt_proxy:
        out.append(ParamsModel(name='post/ngcacher-proxy', value=apt_proxy))

    out.append(ParamsModel(name='access-ssh-root-mode',
                           value='without-password'))
    out.append(ParamsModel(name='kernel-console', value='ttyS1,115200'))
    out.append(ParamsModel(name='select-kickseed',
                           value='snaps-net-seed.tmpl'))

    out.append(ParamsModel(name='access-keys',
                           value={user: public_key, 'root': public_key}))
    return out


def __delete_machines(rebar_session, boot_conf):
    """
    Deletes all of the DHCP reservations for PXE booting
    :param rebar_session: the HTTP session to Digital Rebar
    :param boot_conf: the boot configuration
    :raises Exceptions
    """
    try:
        machines = __instantiate_drp_machines(rebar_session, boot_conf)
        logger.info('Attempting to create DRP machines')
        for machine in machines:
            logger.debug('Attempting to delete DRP machine %s', machine)
            machine.delete()
    except Exception as e:
        logger.warn('Unable to delete all machines - [%s]', e)


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
            pxe_conf = pxe_confs[0]
        else:
            pxe_conf = pxe_confs
    else:
        pxe_conf = tftp_conf

    for host_conf in host_confs:
        drp_mach_conf = __get_drb_machine_config(
            host_conf, pxe_conf, bind_hosts_confs)
        if drp_mach_conf:
            logger.info('Creating machine object [%s]', drp_mach_conf)
            out.append(Machine(rebar_session, drp_mach_conf))

    return out


def __get_drb_machine_config(host_conf, pxe_conf, bind_host_confs):
    mac = None
    for bind_host_conf in bind_host_confs:
        if bind_host_conf['ip'] == host_conf['access_ip']:
            mac = bind_host_conf['mac']

    if 'ubuntu' in pxe_conf:
        boot_os = 'ubuntu-18.04.3-server-amd64.iso'
    else:
        raise Exception('Ubuntu is currently only supported')

    if mac:
        # TODO/FIXME - os and workflow must be hardcoded now
        drp_mach_dict = {
            'ip': host_conf['access_ip'],
            'mac': mac,
            'name': host_conf['name'],
            'os': boot_os,
            'type': 'snaps-boot',
            'workflow': 'snaps-ubuntu-18.04-hwe'
        }

        logger.info('Instantiating a MachineModel object with %s',
                    drp_mach_dict)

        return MachineModel(**drp_mach_dict)
    else:
        logger.warn('Unable to create machine with os [%s] and mac [%s]',
                    boot_os, mac)
