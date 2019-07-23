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
variable "build_id" {}

# Variables that are recommended to change as they won't work in all envs
variable "public_key_file" {default = "~/.ssh/id_rsa.pub"}
variable "private_key_file" {default = "~/.ssh/id_rsa"}

# Optional Variables for Cloud
variable "sudo_user" {default = "ubuntu"}
variable "region" {default = "us-west-2"}
variable "availability_zone" {default = "us-west-2b"}

# Optional Variables for test
variable "src_copy_dir" {default = "/tmp"}
# TODO - add in some logic into this default post_script file as it does nothing
variable "post_script_file" {default = "/tmp/snaps-boot/ci/scripts/post_script"}
variable "priv_ip_prfx" {default = "10.0.1"}
variable "admin_ip_prfx" {default = "10.0.2"}
variable "pub_ip_prfx" {default = "10.0.3"}

# Ubuntu 16.04 SSD Volume Type
//variable "ami" {default = "ami-0b37e9efc396e4c38"}
# Ubuntu 18.04 SSD Volume Type
variable "ami" {default = "ami-07b4f3c02c7f83d59"}

# snaps-boot image with KVM and generic.qcow2
//variable "ami" {default = "ami-044440dc7a3d75d2b"}
variable "instance_type" {default = "t2.2xlarge"}

# Playbook Constants
variable "ANSIBLE_CMD" {default = "export ANSIBLE_HOST_KEY_CHECKING=False; ansible-playbook"}
variable "SETUP_KVM_DEPENDENCIES" {default = "../../playbooks/kvm/dependencies.yaml"}
variable "SETUP_KVM_NETWORKS" {default = "../../playbooks/kvm/networks.yaml"}
variable "SETUP_KVM_SERVERS" {default = "../../playbooks/kvm/servers.yaml"}
variable "EXE_SNAPS_BOOT_PB" {default = "../../playbooks/setup_build.yaml"}
