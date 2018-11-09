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
import mock
import sys
import unittest

import pkg_resources
from snaps_common.file import file_utils

from snaps_boot.provision import ipmi_utils

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class IpmiUtilsTests(unittest.TestCase):
    """
    Tests functions in snaps_boot.provision.ipmi_utils
    To run these tests, install docker to localhost then run:
    docker run --name ipmi-emulator -p 623:623/udp vaporio/ipmi-emulator-x64
    Found this @ https://opendcre-docs.readthedocs.io/en/latest/emulators.html
    """

    def setUp(self):
        conf_file = pkg_resources.resource_filename('tests.conf', 'hosts.yaml')
        self.boot_conf = file_utils.read_yaml(conf_file)

    @mock.patch('snaps_boot.provision.ipmi_utils.get_ipmi_creds',
                return_value=([('localhost', 'ADMIN', 'ADMIN')]))
    def test_reboot_pxe(self, m1):
        """
        Tests the ipmi_utils#reboot_pxe.
        :return:
        """
        ipmi_utils.reboot_pxe(self.boot_conf)

    @mock.patch('snaps_boot.provision.ipmi_utils.get_ipmi_creds',
                return_value=([('localhost', 'ADMIN', 'ADMIN')]))
    def test_reboot_disk(self, m1):
        """
        Tests the ipmi_utils#reboot_pxe.
        :return:
        """
        ipmi_utils.reboot_disk(self.boot_conf)

    def test_get_ipmi_creds(self):
        conf_file = pkg_resources.resource_filename('tests.conf', 'hosts.yaml')
        conf = file_utils.read_yaml(conf_file)
        creds = ipmi_utils.get_ipmi_creds(conf)
        self.assertEqual(5, len(creds))
