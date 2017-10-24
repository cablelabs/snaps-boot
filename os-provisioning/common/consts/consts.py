# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG S.à.r.l. and Cable Television Laboratories, Inc.
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

"""
Constants.py
"""
import os
from pathlib import Path
p = str(Path(__file__).parents[2])

CWD= p + "/"
print "CWD_IAAS path is exported implicitly"
print CWD
KEY_IP_LIST = []
ANSIBLE_PATH=CWD+"ansible_p/"
DEVSTACK_YAML=ANSIBLE_PATH+"commission/openstack/playbooks/deploy_mode/devstack/"
OPENSTACK = "openstack"
DEPLOYMENT_TYPE="deployement_type"
PROXIES = "proxies"
HTTP_PROXY = "http_proxy"
HTTPS_PROXY = "https_proxy"
FTP_PROXY = "ftp_proxy"
NO_PROXY = "no_proxy"
HOSTS = "hosts"
HOST = "host"
INTERFACES = "interfaces"
INTERFACE = "interface"
NODE_TYPE = "node_type"
IP = "ip"
TYPE = "type"
GIT_BRANCH = "git_branch"
SERVICE_PASSWORD = "service_password"
SERVICE_HOST = "service_host"
HOSTNAME = "hostname"
SAMPLEDIR = "packages/source/samples/"
LOCALDIR = "packages/source/locals/"
LOCAL_ALL = "local_all.conf"
LOCAL_COMPUTE = "local_compute.conf"
LOCAL_CONTROLLER = "local_controller.conf"
NAME="name"
USER="user"
PASSWORD="password"
HOSTS_FILE="/etc/ansible/hosts"
ANSIBLE_CONF="/etc/ansible/ansible.cfg"
PROXY_DATA_FILE=ANSIBLE_PATH+"ansible_utils/proxy_data.yaml"
VARIABLE_FILE=ANSIBLE_PATH+"ansible_utils/variable.yaml"
DEVSTACK_PREPARATION_FILE=DEVSTACK_YAML+"devstack_preparation.yaml"
DEVSTACK_LAUNCH_FILE=DEVSTACK_YAML+"devstack_launch.yaml"
DEVSTACK_SET_HOSTS=DEVSTACK_YAML+"devstack_sethosts.yaml"
MAC = "mac"
GATEWAY = "gateway"
DEVSTACK_CLEAN_FILE= DEVSTACK_YAML+"devstack_clean.yaml"
PROXY_PATH=CWD+"ansible_p/ansible_utils/proxy_data.yaml"
BASE_SIZE="base_size"
COUNT="count"
KOLLA="kolla"
#-------------------------------------------------------------------------------------
# local conf services constants
#-------------------------------------------------------------------------------------

CORE_COMPONENT = """
[[local|localrc]]
LOGFILE=/opt/stack/logs/stack.sh.log
VERBOSE=True
SCREEN_LOGDIR=/opt/stack/logs
SERVICE_TOKEN={PASSWORD}
ADMIN_PASSWORD={PASSWORD}
MYSQL_PASSWORD={PASSWORD}
SERVICE_PASSWORD={PASSWORD}
DATABASE_PASSWORD={PASSWORD}
RABBIT_PASSWORD={PASSWORD}
RECLONE=yes

KEYSTONE_BRANCH={BRANCH}
NOVA_BRANCH={BRANCH}
NEUTRON_BRANCH={BRANCH}
GLANCE_BRANCH={BRANCH}
HEAT_BRANCH={BRANCH}
HORIZON_BRANCH={BRANCH}
HOST_IP={HOST_IP}
PUBLIC_INTERFACE={PUBLIC_INTERFACE}

SERVICE_HOST={SERVICE_HOST_IP}
MYSQL_HOST={SERVICE_HOST_IP}
RABBIT_HOST={SERVICE_HOST_IP}
GLANCE_HOSTPORT={SERVICE_HOST_IP}:9292

"""

CORE_SERVICES="""

ENABLED_SERVICES=rabbit
enable_service q-agt
VIRT_DRIVER=libvirt
LIBVIRT_TYPE=kvm
"""

CORE_CONTROLLER="""
ENABLED_SERVICES+=,mysql,key
ENABLED_SERVICES+=,n-api,n-crt,n-obj,n-cond,n-sch,n-cauth
ENABLED_SERVICES+=,g-api,g-reg
ENABLED_SERVICES+=,horizon
enable_service heat,h-api,h-api-cfn,h-api-cw,h-eng
#SFC
enable_plugin networking-sfc https://git.openstack.org/openstack/networking-sfc {BRANCH}
"""

CORE_DISABLE="""
disable_all_services
"""

NOVA_COMPUTE="""
ENABLED_SERVICES+=,n-cpu,n-novnc
"""

NEUTRON="""
enable_service q-svc
enable_service q-dhcp
enable_service q-l3
enable_service q-meta
enable_service neutron
"""

NEUTRON_NETWORKS="""
FLOATING_RANGE={EXT_SUB}
FIXED_RANGE={TENANT_SUB}
FIXED_NETWORK_SIZE={TENANT_SUB_SIZE}
Q_FLOATING_ALLOCATION_POOL=start={EXT_POOL_START},end={EXT_POOL_END}
PUBLIC_NETWORK_GATEWAY={EXT_GATEWAY}
"""

NEUTRON_AGENT="""
enable_service q-agt
"""

TELEMETRY="""
enable_service ceilometer-acompute ceilometer-acentral ceilometer-collector ceilometer-api
"""
TELEMETRY_AGENT="""
enable_service ceilometer-acompute
"""

STORAGE_CONTROLLER="""
ENABLED_SERVICES+=,cinder,c-sch,c-api
"""

STORAGE_COMPUTE="""
ENABLED_SERVICES+=,c-vol,c-bak
VOLUME_GROUP="stack-volumes"
VOLUME_NAME_PREFIX="volume-"
VOLUME_BACKING_FILE_SIZE=20500M

[[post-config|/etc/cinder/cinder.conf]]
[database]
connection = mysql+pymysql://root:{PASSWORD}@{SERVICE_HOST_IP}/cinder?charset=utf8
"""

MAGNUM="""
enable_plugin magnum https://git.openstack.org/openstack/magnum {BRANCH}
enable_plugin magnum-ui https://github.com/openstack/magnum-ui {BRANCH}
"""

TEMPEST="""
disable_service tempest
"""


SERVICES="services"

BASE_DISTRIBUTION="base_distro"
INSTALL_TYPE="install_type"
KEEPALIVED_VIRTUAL_ROUTER_ID="keepalived_virtual_router_id"
INTERNAL_VIP_ADDRESS="internal_vip_address"
INTERNAL_INTERFACE="internal_interface"
EXTERNAL_VIP_ADDRESS="external_vip_address"
EXTERNAL_INTERFACE="external_interface"
REGISTRY="kolla_registry"


KOLLA_SOURCE_PATH=CWD+"packages/source/"

DAEMON_FILE=KOLLA_SOURCE_PATH+"daemon.json"
GLOBAL_BASE_FILE=KOLLA_SOURCE_PATH+"globals_bak.yml"
GLOBAL_FILE=KOLLA_SOURCE_PATH+"globals.yml"
NETVAR_FILE=KOLLA_SOURCE_PATH+"netvars.yml"
INVENTORY_SOURCE_FOLDER=KOLLA_SOURCE_PATH+"inventory/"
INVENTORY_MULTINODE_BASE_FILE=INVENTORY_SOURCE_FOLDER+"multinode_bak"
INVENTORY_MULTINODE_FILE=INVENTORY_SOURCE_FOLDER+"multinode"


KOLLA_YAML=ANSIBLE_PATH+"commission/openstack/playbooks/deploy_mode/kolla/"
SINGLE_NODE_KOLLA_YAML=KOLLA_YAML+"single_node_kolla_newton.yaml"
MULTI_NODE_KOLLA_COMPUTE_YAML=KOLLA_YAML+"multinode_kolla_compute_newton.yaml"
MULTI_NODE_KOLLA_ISO_NWK_YAML=KOLLA_YAML+"multinode_kolla_iso_network.yaml"
MULTI_NODE_KOLLA_CONTROLLER_YAML=KOLLA_YAML+"multinode_kolla_controller_newton.yaml"
KOLLA_SET_HOSTS=KOLLA_YAML+"kolla_sethosts.yaml"
KOLLA_SET_HOSTSNAME=KOLLA_YAML+"kolla_sethostsname.yaml"
SINGLE_NODE_KOLLA_YAML=KOLLA_YAML+"single_node_kolla_newton.yaml"
KOLLA_SET_REGISTRY=KOLLA_YAML+"setup_registry.yaml"
KOLLA_SET_KOLLA=KOLLA_YAML+"setup_kolla.yaml"
KOLLA_SET_STORAGE=KOLLA_YAML+"setup_storage.yaml"
KOLLA_CLEANUP_HOSTS=KOLLA_YAML+"cleanup_hosts.yaml"
KOLLA_REMOVE_REGISTRY=KOLLA_YAML+"remove_registry.yaml"
KOLLA_REMOVE_STORAGE=KOLLA_YAML+"cleanup_storage.yaml"
KOLLA_COPY_KEY=KOLLA_YAML+"copy_key_gen.yaml"
KOLLA_PUSH_KEY=KOLLA_YAML+"push_key_gen.yaml"
KOLLA_REMOVE_IMAGES=KOLLA_YAML+"remove_images.yaml"
KOLLA_SET_PIN=KOLLA_YAML+"kolla_set_pin.yaml"
KOLLA_CEPH_SETUP=KOLLA_YAML+"ceph_setup.yaml"
DOCKER_LIST_SRC=KOLLA_SOURCE_PATH+"docker.list"
HTTP_PROXY_SRC=KOLLA_SOURCE_PATH+"http-proxy_bak.conf"
KOLLA_CONF_SRC=KOLLA_SOURCE_PATH+"kolla.conf"
INVENTORY_SRC=KOLLA_SOURCE_PATH+"inventory"
SSH_PATH="/root/.ssh"
KOLLA_REGISTRY_PORT="kolla_registry_port"
