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
import argparse
import unittest

import mock

import iaas_launch


class IaasLaunchTests(unittest.TestCase):
    """
    Ensures the iaas_launch.py does not have any glaring syntax errors.
    """

    def setUp(self):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('-log_level', type=str)
        self.parser.add_argument('-config', type=str)
        self.parser.add_argument('-hardware', type=str)
        self.parser.add_argument('-provisionClean', type=str)
        self.parser.add_argument('-staticIPCleanup', type=str)
        self.parser.add_argument('-staticIPConfigure', type=str)
        self.parser.add_argument('-boot', type=str)
        self.parser.add_argument('-bootd', type=str)
        self.parser.add_argument('-setIsolCpus', type=str)
        self.parser.add_argument('-delIsolCpus', type=str)

    def test_main_minimal_args(self):
        """
        Basic tests of the main() function of iaas_launch.py with the minimal
        number of arguments. This test basically checks the imports and basic
        syntax
        :return:
        """

        parsed = self.parser.parse_args([
            '-log_level', 'DEBUG',
            '-config', 'foo',
            '-hardware', iaas_launch.ARG_NOT_SET,
            '-provisionClean', iaas_launch.ARG_NOT_SET,
            '-staticIPCleanup', iaas_launch.ARG_NOT_SET,
            '-staticIPConfigure', iaas_launch.ARG_NOT_SET,
            '-boot', iaas_launch.ARG_NOT_SET,
            '-bootd', iaas_launch.ARG_NOT_SET,
            '-setIsolCpus', iaas_launch.ARG_NOT_SET,
            '-delIsolCpus', iaas_launch.ARG_NOT_SET,
        ])
        self.assertEqual(parsed.log_level, 'DEBUG')

        config = {'foo': 'bar'}
        with mock.patch('os.path.dirname', return_value='/'),\
                mock.patch('snaps_common.file.file_utils.read_yaml',
                           return_value=config):
            iaas_launch.main(parsed)
