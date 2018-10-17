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
import sys
import unittest

import mock
import pkg_resources
from snaps_common.file import file_utils

from snaps_boot.provision import rebar_utils

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class RebarUtilsTests(unittest.TestCase):
    """
    Tests function snaps_boot.provision.hardware.digitalrebar#rebar_utils
    """
    @mock.patch('os.system', return_value=0)
    @mock.patch('drp_python.translation_layer.api_http.ApiHttp.open')
    @mock.patch('drp_python.translation_layer.subnets_translation.'
                'SubnetTranslation.get_subnet')
    @mock.patch('drp_python.subnet.Subnet.create')
    @mock.patch('drp_python.machine.Machine.create')
    @mock.patch('drp_python.machine.Machine.get')
    @mock.patch('drp_python.reservation.Reservation.__init__',
                return_value=None)
    @mock.patch('drp_python.reservation.Reservation.create')
    @mock.patch('snaps_common.ansible_snaps.ansible_utils.apply_playbook')
    @mock.patch('time.sleep')
    def test_setup_dhcp_service(self, m1, m2, m3, m4, m5, m6, m7, m8, m9,m10):
        """
        Tests the rebar_utils.
        :return:
        """
        conf_file = pkg_resources.resource_filename('tests.conf', 'hosts.yaml')
        conf = file_utils.read_yaml(conf_file)
        rebar_utils.setup_dhcp_service(None, conf)
