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

locals {
  remote_pub_key_file = "/tmp/${var.build_id}-remote-pk"
}

# Call ensure SSH key has correct permissions
resource "null_resource" "snaps-boot-remote-key-gen" {
  depends_on = [null_resource.snaps-boot-pk-setup]
  provisioner "remote-exec" {
    inline = [
      "ssh-keygen -t rsa -N '' -f ${var.vm_host_priv_key}",
      "sudo cp ${var.vm_host_priv_key} /root/.ssh/",
      "sudo cp ${var.vm_host_priv_key}.pub /root/.ssh/",
    ]
  }
  connection {
    host = aws_instance.snaps-boot-host.public_ip
    type     = "ssh"
    user     = var.sudo_user
    private_key = file(var.private_key_file)
  }
}

# Call ensure SSH key has correct permissions
resource "null_resource" "snaps-boot-get-host-pub-key" {
  depends_on = [null_resource.snaps-boot-remote-key-gen]
  provisioner "local-exec" {
    command = "scp ${var.sudo_user}@${aws_instance.snaps-boot-host.public_ip}:~/.ssh/id_rsa.pub ${local.remote_pub_key_file}"
  }
}

# Call ansible scripts to setup KVM
resource "null_resource" "snaps-boot-proxy-setup" {
  depends_on = [null_resource.snaps-boot-pk-setup]

  # Install KVM dependencies
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-host.public_ip}, \
${var.SETUP_HOST_PROXY} \
--key-file ${var.private_key_file} \
EOT
  }
}

# Call ansible scripts to setup KVM
resource "null_resource" "snaps-boot-kvm-setup" {
  depends_on = [null_resource.snaps-boot-pk-setup]

  # Install KVM dependencies
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-host.public_ip}, \
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
-i ${aws_instance.snaps-boot-host.public_ip}, \
${var.SETUP_KVM_NETWORKS} \
--key-file ${var.private_key_file} \
--extra-vars "\
build_ip_prfx=${var.build_ip_prfx}
build_vm_name=${var.build_vm_name}
build_mac_1=${var.build_mac_1}
build_vm_ip=${var.build_ip_prfx}.${var.build_ip_suffix}
build_net_name=${var.build_net_name}
priv_ip_prfx=${var.priv_ip_prfx}
priv_net_name=${var.priv_net_name}
admin_ip_prfx=${var.admin_ip_prfx}
admin_net_name=${var.admin_net_name}
pub_ip_prfx=${var.pub_ip_prfx}
pub_net_name=${var.pub_net_name}
netmask=${var.netmask}
"\
EOT
  }
}

# Call ansible scripts to setup KVM servers
resource "null_resource" "snaps-boot-server-setup" {
  depends_on = [null_resource.snaps-boot-network-setup,
                null_resource.snaps-boot-get-host-pub-key]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-host.public_ip}, \
${var.SETUP_KVM_SERVERS} \
--key-file ${var.private_key_file} \
--extra-vars "\
pxe_img=/var/lib/libvirt/images/libvirt-pxe.qcow2
target_user=${var.sudo_user}
build_net_name=${var.build_net_name}
priv_net_name=${var.priv_net_name}
priv_ip_prfx=${var.priv_ip_prfx}
admin_net_name=${var.admin_net_name}
admin_ip_prfx=${var.admin_ip_prfx}
pub_net_name=${var.pub_net_name}
pub_ip_prfx=${var.pub_ip_prfx}
build_vm_name=${var.build_vm_name}
build_password=${var.build_password}
build_public_key_file=${local.remote_pub_key_file}
build_ip_prfx=${var.build_ip_prfx}
build_ip_sfx=${var.build_ip_suffix}
build_ip_bits=${var.build_ip_bits}
build_gateway=${var.build_ip_prfx}.1
build_nic_name=${var.build_nic}
build_mac_0=${var.build_mac_0}
build_mac_1=${var.build_mac_1}
build_mac_2=${var.build_mac_2}
build_mac_3=${var.build_mac_3}
node_1_mac_1=${var.node_1_mac_1}
node_1_mac_2=${var.node_1_mac_2}
node_1_mac_3=${var.node_1_mac_3}
node_2_mac_1=${var.node_2_mac_1}
node_2_mac_2=${var.node_2_mac_2}
node_2_mac_3=${var.node_2_mac_3}
node_3_mac_1=${var.node_3_mac_1}
node_3_mac_2=${var.node_3_mac_2}
node_3_mac_3=${var.node_3_mac_3}
"\
EOT
  }
}

//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-src-setup" {
//  depends_on = [null_resource.snaps-boot-server-setup, null_resource.snaps-boot-proxy-setup]
////  depends_on = [null_resource.snaps-boot-kvm-setup]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.SETUP_SRC} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//src_copy_dir=${var.src_copy_dir} \
//"\
//EOT
//  }
//}
//
//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-drp-setup" {
//  depends_on = [null_resource.snaps-boot-src-setup]
////  depends_on = [null_resource.snaps-boot-kvm-setup]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.SETUP_DRP} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//src_copy_dir=${var.src_copy_dir} \
//post_script_file=${var.post_script_file} \
//priv_ip_prfx=${var.priv_ip_prfx} \
//admin_ip_prfx=${var.admin_ip_prfx} \
//pub_ip_prfx=${var.pub_ip_prfx} \
//ip_suffix_1=11 \
//ip_suffix_2=12 \
//ip_suffix_3=13 \
//admin_mac_1=foo-mac-1 \
//admin_mac_2=foo-mac-2 \
//admin_mac_3=foo-mac-3 \
//pub_gateway=foo-gateway \
//broadcast_addr=foo-broadcast_addr \
//domain_name=foo-domain_name \
//dns_addr=8.8.8.8 \
//listen_iface=foo-listen_iface \
//max_lease=7200 \
//netmask=foo-netmask \
//router_ip=foo-router_ip \
//build_admin_ip=foo-build_admin_ip \
//http_proxy_port=3142 \
//priv_addr=foo \
//priv_iface=eth0 \
//admin_iface=eth1 \
//admin_iface=eth2 \
//pxe_pass=foo-pxe_pass \
//hosts_yaml_path=foo-hosts_yaml_path
//"\
//EOT
//  }
//}
//
//resource "null_resource" "snaps-boot-nodes-power-cycle" {
//  depends_on = [null_resource.snaps-boot-drp-setup]
//  provisioner "local-exec" {
//    command = "virsh reset node-1; virsh reset node-2; virsh reset node-3"
//  }
//}
//
//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-verify-intfs-node-1-priv" {
//  depends_on = [null_resource.snaps-boot-nodes-power-cycle]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.VERIFY_INTFS} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//run_as_root=False \
//snaps_boot_dir=${var.src_copy_dir}/snaps-boot \
//check_file=${var.VERIFY_INTFS_CHECK_FILE} \
//username=${var.sudo_user} \
//ip_addr=${var.priv_ip_prfx}.11 \
//src_copy_dir=${var.src_copy_dir} \
//timeout=1800 \
//"\
//EOT
//  }
//}
//
//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-verify-intfs-node-1-admin" {
//  depends_on = [null_resource.snaps-boot-nodes-power-cycle]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.VERIFY_INTFS} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//run_as_root=False \
//snaps_boot_dir=${var.src_copy_dir}/snaps-boot \
//check_file=${var.VERIFY_INTFS_CHECK_FILE} \
//username=${var.sudo_user} \
//ip_addr=${var.admin_ip_prfx}.11 \
//src_copy_dir=${var.src_copy_dir} \
//timeout=1800 \
//"\
//EOT
//  }
//}
//
//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-verify-intfs-node-1-pub" {
//  depends_on = [null_resource.snaps-boot-nodes-power-cycle]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.VERIFY_INTFS} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//run_as_root=False \
//snaps_boot_dir=${var.src_copy_dir}/snaps-boot \
//check_file=${var.VERIFY_INTFS_CHECK_FILE} \
//username=${var.sudo_user} \
//ip_addr=${var.pub_ip_prfx}.11 \
//src_copy_dir=${var.src_copy_dir} \
//timeout=1800 \
//"\
//EOT
//  }
//}
//
//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-verify-intfs-node-2-priv" {
//  depends_on = [null_resource.snaps-boot-nodes-power-cycle]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.VERIFY_INTFS} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//run_as_root=False \
//snaps_boot_dir=${var.src_copy_dir}/snaps-boot \
//check_file=${var.VERIFY_INTFS_CHECK_FILE} \
//username=${var.sudo_user} \
//ip_addr=${var.priv_ip_prfx}.12 \
//src_copy_dir=${var.src_copy_dir} \
//timeout=1800 \
//"\
//EOT
//  }
//}
//
//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-verify-intfs-node-2-admin" {
//  depends_on = [null_resource.snaps-boot-nodes-power-cycle]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.VERIFY_INTFS} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//run_as_root=False \
//snaps_boot_dir=${var.src_copy_dir}/snaps-boot \
//check_file=${var.VERIFY_INTFS_CHECK_FILE} \
//username=${var.sudo_user} \
//ip_addr=${var.admin_ip_prfx}.12 \
//src_copy_dir=${var.src_copy_dir} \
//timeout=1800 \
//"\
//EOT
//  }
//}
//
//# Call ansible scripts to run snaps-boot
//resource "null_resource" "snaps-boot-verify-intfs-node-2-pub" {
//  depends_on = [null_resource.snaps-boot-nodes-power-cycle]
//
//  # Setup KVM on the VM to create VMs on it for testing snaps-boot
//  provisioner "local-exec" {
//    command = <<EOT
//${var.ANSIBLE_CMD} -u ${var.sudo_user} \
//-i ${aws_instance.snaps-boot-build.public_ip}, \
//${var.VERIFY_INTFS} \
//--key-file ${var.private_key_file} \
//--extra-vars "\
//run_as_root=False \
//snaps_boot_dir=${var.src_copy_dir}/snaps-boot \
//check_file=${var.VERIFY_INTFS_CHECK_FILE} \
//username=${var.sudo_user} \
//ip_addr=${var.pub_ip_prfx}.12 \
//src_copy_dir=${var.src_copy_dir} \
//timeout=1800 \
//"\
//EOT
//  }
//}
