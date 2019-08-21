# Copyright (c) 2019 Cable Television Laboratories, Inc.
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

# Required Variables
variable "access_key" {}
variable "secret_key" {}
variable "git_user" {}
variable "git_pass" {}
variable "build_id" {}

# Variables that are recommended to change as they won't work in all envs
variable "public_key_file" {default = "~/.ssh/id_rsa.pub"}
variable "private_key_file" {default = "~/.ssh/id_rsa"}

# Optional Variables for Cloud
variable "spot_type" {default = "one-time"}
// Set wait_for_fulfillment to true in order to obtain instance attributes
variable "wait_for_fulfillment" {default = "true"}

# Playbook Constants
variable "ANSIBLE_CMD" {default = "export ANSIBLE_HOST_KEY_CHECKING=False; ansible-playbook"}
variable "WAIT_FOR_BUILD" {default = "../playbooks/wait_for_build.yaml"}
variable "SETUP_SRC" {default = "../playbooks/setup_src.yaml"}
variable "SETUP_DRP" {default = "../playbooks/setup_drp.yaml"}
variable "VERIFY_INTFS" {default = "../playbooks/verify_intfs.yaml"}
variable "VERIFY_APT_PROXY" {default = "../playbooks/verify_apt.yaml"}
variable "CONFIG_INTFS" {default = "../playbooks/config_intfs.yaml"}
variable "VERIFY_INTFS_CHECK_FILE" {default = "/var/log/hello_world"}

# Optional Variables for test
variable "src_copy_dir" {default = "/tmp"}
variable "post_script_file" {default = "/tmp/snaps-boot/ci/scripts/post_script"}
variable "hosts_yaml_path" {default = "/tmp/hosts.yaml"}

# best to obtain from snaps-config/ci/snaps-boot-env/boot-env.tfvars
variable "initial_boot_timeout" {}
variable "std_boot_timeout" {}
variable "boot_ami" {}
variable "sudo_user" {}
variable "region" {}
variable "availability_zone" {}
variable "instance_type" {}
variable "volume_size" {}
variable "netmask" {}
variable "build_ip_prfx" {}
variable "build_ip_bits" {}
variable "build_ip_suffix" {}
variable "build_net_name" {}
variable "priv_ip_prfx" {}
variable "priv_net_name" {}
variable "admin_ip_prfx" {}
variable "admin_net_name" {}
variable "pub_ip_prfx" {}
variable "pub_net_name" {}
variable "build_nic" {}
variable "build_vm_name" {}
variable "build_password" {}
variable "build_mac_0" {}
variable "build_mac_1" {}
variable "build_mac_2" {}
variable "build_mac_3" {}
variable "node_1_name" {}
variable "node_2_name" {}
variable "node_3_name" {}
variable "node_1_mac_1" {}
variable "node_1_mac_2" {}
variable "node_1_mac_3" {}
variable "node_2_mac_1" {}
variable "node_2_mac_2" {}
variable "node_2_mac_3" {}
variable "node_3_mac_1" {}
variable "node_3_mac_2" {}
variable "node_3_mac_3" {}
variable "node_1_suffix" {}
variable "node_2_suffix" {}
variable "node_3_suffix" {}
variable "proxy_port" {}
variable "ngcacher_proxy_port" {}
variable "pxe_pass" {}
