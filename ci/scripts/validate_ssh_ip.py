#!/usr/bin/python
#
# Copyright (c) 2017 Cable Television Laboratories, Inc. ("CableLabs")
#                    and others.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# This script is responsible for deploying virtual environments
import argparse
import logging

import paramiko
import os
import time

__author__ = 'spisarski'

logger = logging.getLogger('validate_intfs')

ARG_NOT_SET = "argument not set"


def main(arguments):
    """
    Parse hosts_file and validate that the interfaces contain the expected
    IP values.
    CWD must be this directory where this script is located.

    :return: To the OS
    """
    logging.basicConfig(level=logging.INFO)

    start = time.time()

    timeout = int(arguments.timeout)

    while timeout > time.time() - start:
        try:
            ssh_client = __ssh_client(
                arguments.ip_addr, arguments.username,
                password=arguments.password,
                priv_key_file=arguments.priv_key_file)
            if ssh_client:
                exit(0)
        except Exception as e:
            logger.info('Retry obtaining connection - %s', e)

        logger.debug('Retry querying VM status in ' + str(
            arguments.poll_interval) + ' seconds')
        time.sleep(arguments.poll_interval)
        logger.debug('VM status query timeout in ' + str(
            timeout - (time.time() - start)))

    logger.error(
        'Timeout checking for SSH connection to %s' + arguments.ip_addr)
    exit(1)


def __ssh_client(ip, user, password=None, priv_key_file=None):
    """
    Retrieves and attemts an SSH connection
    :param ip: the IP of the host to connect
    :param user: the user with which to connect
    :param password: the password (optional)
    :param priv_key_file: the private key file path (optional)
    """
    logger.debug('Retrieving SSH client')
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.MissingHostKeyPolicy())
    ssh.connect(ip, username=user, password=password,
                key_filename=priv_key_file)
    return ssh


if __name__ == '__main__':
    # To ensure any files referenced via a relative path will begin from the
    # directory in which this file resides
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--username', dest='username', required=True,
        help='The username to the hosts to validate')
    parser.add_argument(
        '-p', '--password', dest='password', required=False,
        help='The password to the hosts to validate')
    parser.add_argument(
        '-k', '--priv_key_file', dest='priv_key_file', required=False,
        help='The private key file to the hosts to validate')
    parser.add_argument(
        '-i', '--ip-addr', dest='ip_addr', required=True,
        help='The address to connect')
    parser.add_argument(
        '-t', '--timeout', dest='timeout', default=13600,
        help='The number of seconds to retry')
    parser.add_argument(
        '-pi', '--poll-interval', dest='poll_interval', default=10,
        help='The number of seconds before next retry')
    args = parser.parse_args()

    main(args)
