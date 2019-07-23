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

# Call ensure SSH key has correct permissions
resource "null_resource" "snaps-boot-pk-setup" {
  provisioner "local-exec" {
    command = "chmod 600 ${var.private_key_file}"
  }
}

# Call ansible scripts to setup KVM
resource "null_resource" "snaps-boot-kvm-setup" {
  depends_on = [null_resource.snaps-boot-pk-setup]

  # Install KVM dependencies
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-build.public_ip}, \
${var.SETUP_KVM_DEPENDENCIES} \
--key-file ${var.private_key_file} \
EOT
  }
}

# Call ansible scripts to setup KVM networks
resource "null_resource" "snaps-boot-network-setup" {
  depends_on = [null_resource.snaps-boot-kvm-setup]
  # Create KVM networks
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-build.public_ip}, \
${var.SETUP_KVM_NETWORKS} \
--key-file ${var.private_key_file} \
--extra-vars "\
priv_ip_prfx=${var.priv_ip_prfx} \
admin_ip_prfx=${var.admin_ip_prfx} \
pub_ip_prfx=${var.pub_ip_prfx}
"\
EOT
  }
}

# Call ansible scripts to setup KVM servers
resource "null_resource" "snaps-boot-server-setup" {
  depends_on = [null_resource.snaps-boot-network-setup]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-build.public_ip}, \
${var.SETUP_KVM_SERVERS} \
--key-file ${var.private_key_file} \
--extra-vars "\
aws_access_key=${var.access_key} \
aws_secret_key=${var.secret_key} \
pxe_img=/var/lib/libvirt/images/libvirt-pxe.qcow2
"\
EOT
  }
}

# Call ansible scripts to run snaps-boot
resource "null_resource" "snaps-boot-deploy" {
  depends_on = [null_resource.snaps-boot-server-setup]
//  depends_on = [null_resource.snaps-boot-kvm-setup]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-build.public_ip}, \
${var.EXE_SNAPS_BOOT_PB} \
--key-file ${var.private_key_file} \
--extra-vars "\
src_copy_dir=${var.src_copy_dir} \
post_script_file=${var.post_script_file} \
priv_ip_prfx=10.0.1 \
admin_ip_prfx=10.0.2 \
pub_ip_prfx=10.0.3
ip_suffix_1=11
ip_suffix_2=12
ip_suffix_3=13
admin_mac_1=foo-mac-1
admin_mac_2=foo-mac-2
admin_mac_3=foo-mac-3
pub_gateway=foo-gateway
broadcast_addr=foo-broadcast_addr
domain_name=foo-domain_name
dns_addr=8.8.8.8
listen_iface=foo-listen_iface
max_lease=7200
netmask=foo-netmask
router_ip=foo-router_ip
build_admin_ip=foo-build_admin_ip
http_proxy_port=3142
priv_iface=eth0
admin_iface=eth1
admin_iface=eth2
pxe_pass=foo-pxe_pass
hosts_yaml_path=foo-hosts_yaml_path
"\
EOT
  }
}
