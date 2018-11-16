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
        from snaps_common.ssh import ssh_utils
        try:
            ssh_client = ssh_utils.ssh_client(
                arguments.ip_addr, arguments.username)
            if ssh_client:
                exit(0)
        except Exception as e:
            logger.info('Retry obtaining connection - %s', e)

        logger.debug('Retry querying VM status in ' + str(
            arguments.poll_interval) + ' seconds')
        time.sleep(arguments.poll_interval)
        logger.debug('VM status query timeout in ' + str(
            timeout - (time.time() - start)))

    raise Exception(
        'Timeout checking for SSH connection to {}'.format(arguments.ip_addr))


if __name__ == '__main__':
    # To ensure any files referenced via a relative path will begin from the
    # directory in which this file resides
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-u', '--username', dest='username', required=True,
        help='The username to the hosts to validate')
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
