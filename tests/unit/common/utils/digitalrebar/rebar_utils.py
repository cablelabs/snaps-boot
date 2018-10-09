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
import unittest

from snaps_boot.provision.hardware.digitalrebar import rebar_utils


class RebarUtilsTests(unittest.TestCase):
    """
    Tests function snaps_boot.provision.hardware.digitalrebar#rebar_utils
    """
    def test_setup_dhcp_service(self):
        """
        Tests the rebar_utils.
        :return:
        """
        rebar_utils.setup_dhcp_service(None, None)
