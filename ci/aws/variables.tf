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
variable "sudo_user" {default = "ubuntu"}
variable "region" {default = "us-west-2"}
variable "availability_zone" {default = "us-west-2b"}

# snaps-boot image with KVM and generic.qcow2 TODO DELETE AMI
//variable "ami" {default = "ami-044440dc7a3d75d2b"}
# Ubuntu 16.04 SSD Volume Type
//variable "ami" {default = "ami-0b37e9efc396e4c38"}
# Ubuntu 18.04 SSD Volume Type
variable "ami" {default = "ami-07b4f3c02c7f83d59"}

//variable "instance_type" {default = "t2.2xlarge"}
variable "instance_type" {default = "m5a.8xlarge"}

# Playbook Constants
variable "ANSIBLE_CMD" {default = "export ANSIBLE_HOST_KEY_CHECKING=False; ansible-playbook"}
variable "SETUP_HOST_PROXY" {default = "../playbooks/setup_proxy.yaml"}
variable "SETUP_KVM_DEPENDENCIES" {default = "../playbooks/kvm/dependencies.yaml"}
variable "SETUP_KVM_NETWORKS" {default = "../playbooks/kvm/networks.yaml"}
variable "SETUP_KVM_SERVERS" {default = "../playbooks/kvm/servers.yaml"}
variable "SETUP_SRC" {default = "../playbooks/setup_src.yaml"}
variable "SETUP_DRP" {default = "../playbooks/setup_drp.yaml"}
variable "VERIFY_INTFS" {default = "../playbooks/verify_intfs.yaml"}
variable "VERIFY_INTFS_CHECK_FILE" {default = "/var/log/hello_world"}

# Optional Variables for test
variable "src_copy_dir" {default = "/tmp"}
# TODO - add in some logic into this default post_script file as it does nothing
variable "post_script_file" {default = "/tmp/snaps-boot/ci/scripts/post_script"}
variable "netmask" {default = "255.255.255.0"}
variable "build_ip_prfx" {default = "10.0.0"}
variable "build_ip_bits" {default = "24"}
variable "build_ip_suffix" {default = "5"}
variable "build_net_name" {default = "build-net"}
variable "priv_ip_prfx" {default = "10.0.1"}
variable "priv_net_name" {default = "priv-net"}
variable "admin_ip_prfx" {default = "10.0.2"}
variable "admin_net_name" {default = "admin-net"}
variable "pub_ip_prfx" {default = "10.0.3"}
variable "pub_net_name" {default = "pub-net"}
variable "build_nic" {default = "ens3"}
variable "build_vm_name" {default = "build_server"}
variable "build_password" {default = "password"}
variable "build_mac_0" {default = "00:00:00:00:00:00"}
variable "build_mac_1" {default = "00:00:00:00:00:01"}
variable "build_mac_2" {default = "00:00:00:00:00:02"}
variable "build_mac_3" {default = "00:00:00:00:00:03"}
variable "node_1_mac_1" {default = "00:00:00:00:01:01"}
variable "node_1_mac_2" {default = "00:00:00:00:01:02"}
variable "node_1_mac_3" {default = "00:00:00:00:01:03"}
variable "node_2_mac_1" {default = "00:00:00:00:02:01"}
variable "node_2_mac_2" {default = "00:00:00:00:02:02"}
variable "node_2_mac_3" {default = "00:00:00:00:02:03"}
variable "node_3_mac_1" {default = "00:00:00:00:03:01"}
variable "node_3_mac_2" {default = "00:00:00:00:03:02"}
variable "node_3_mac_3" {default = "00:00:00:00:03:03"}
variable "proxy_port" {default = "3128"}

variable "vm_host_pub_key" {default = "~/.ssh/id_rsa.pub"}
variable "vm_host_priv_key" {default = "~/.ssh/id_rsa"}