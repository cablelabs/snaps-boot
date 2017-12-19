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

import pkg_resources
from snaps_boot.common.utils import file_utils


class FileUtilsTests(unittest.TestCase):
    """
    Tests for functions located in file_utils
    """

    def test_parse_yaml(self):
        """
        Test to ensure a YAML file is properly parsed
        :return:
        """
        yaml_filepath = pkg_resources.resource_filename(
            'tests.unit.common.utils', 'test.yaml')
        parsed_dict = file_utils.read_yaml(yaml_filepath)
        self.assertEqual(2, len(parsed_dict))
        self.assertTrue('foo' in parsed_dict)
        self.assertTrue('hello' in parsed_dict)

        hello_dict = parsed_dict['hello']
        self.assertEqual(1, len(hello_dict))
        self.assertTrue('world' in hello_dict)
        self.assertTrue('earth', hello_dict['world'])

    def test_parse_text_file(self):
        """
        Tests attempting to parse a text file. The utility returns the contents
        of the text file back as a str, not a dict
        :return:
        """
        text_filepath = pkg_resources.resource_filename(
            'tests.unit.common.utils', 'test.txt')

        out = file_utils.read_yaml(text_filepath)
        self.assertTrue(isinstance(out, str))

    def test_parse_no_file(self):
        """
        Test to ensure an IOError is raised when reading in a non-existent
        file
        :return:
        """
        with self.assertRaises(IOError):
            file_utils.read_yaml('foo')
