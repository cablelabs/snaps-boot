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
import json
import requests


def setup_dhcp_service(boot_conf):
    """
    Creates a DHCP service
    :param boot_conf: the configuration
    """
    subnet_conf = __generate_subnet_config(boot_conf)
    url = None
    data = json.dumps(subnet_conf)
    response = requests.post(url, data=data)


def __generate_subnet_config(boot_conf):
    """
    Returns a dict containing the
    :param boot_conf:
    :return:
    """
    cidr = None
    start = None
    end = None
    gateway = None
    dns = None
    domain = None

    return """
    {
        "Name": "local_subnet",
        "Subnet": "{0}",
        "ActiveStart": "{1}",
        "ActiveEnd": "{2}",
        "ActiveLeaseTime": 60,
        "Enabled": true,
        "ReservedLeaseTime": 7200,
        "Strategy": "MAC",
        "Options": [
            { "Code": 3, "Value": "{3}", "Description": "Default Gateway" },
            { "Code": 6, "Value": "{4}", "Description": "DNS Servers" },
            { "Code": 15, "Value": "{5}", "Description": "Domain Name" }
        ]
    }
    """.format(cidr, start, end, gateway, dns, domain)
