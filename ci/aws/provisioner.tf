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
  remote_pub_key_file = "/tmp/${var.build_id}-remote-pk.pub"
  remote_priv_key_file = "/tmp/${var.build_id}-remote-pk"
}

# Call ensure SSH key has correct permissions
resource "null_resource" "snaps-boot-remote-key-gen" {
  depends_on = [null_resource.snaps-boot-pk-setup]
  provisioner "remote-exec" {
    inline = [
      "ssh-keygen -t rsa -N '' -f ${var.vm_host_priv_key}",
    ]
  }
  connection {
    host = aws_spot_instance_request.snaps-boot-host.public_ip
    type     = "ssh"
    user     = var.sudo_user
    private_key = file(var.private_key_file)
  }
}

# Call ensure SSH key has correct permissions
resource "null_resource" "snaps-boot-get-host-pub-key" {
  depends_on = [null_resource.snaps-boot-remote-key-gen]
  provisioner "local-exec" {
    command = "scp -o StrictHostKeyChecking=no ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip}:~/.ssh/id_rsa.pub ${local.remote_pub_key_file}"
  }
}

# Call ensure SSH key has correct permissions
resource "null_resource" "snaps-boot-get-host-priv-key" {
  depends_on = [null_resource.snaps-boot-remote-key-gen]
  provisioner "local-exec" {
    command = "scp -o StrictHostKeyChecking=no ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip}:~/.ssh/id_rsa ${local.remote_priv_key_file}"
  }
}

# Call ansible scripts to setup KVM
resource "null_resource" "snaps-boot-proxy-setup" {
  depends_on = [null_resource.snaps-boot-get-host-pub-key]

  # Install KVM dependencies
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_spot_instance_request.snaps-boot-host.public_ip}, \
${var.SETUP_HOST_PROXY} \
--key-file ${var.private_key_file} \
--extra-vars "\
proxy_port=${var.proxy_port}
"\
EOT
  }
}

# Call ansible scripts to setup KVM
resource "null_resource" "snaps-boot-kvm-setup" {
  depends_on = [null_resource.snaps-boot-proxy-setup]

  # Install KVM dependencies
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_spot_instance_request.snaps-boot-host.public_ip}, \
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
-i ${aws_spot_instance_request.snaps-boot-host.public_ip}, \
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
-i ${aws_spot_instance_request.snaps-boot-host.public_ip}, \
${var.SETUP_KVM_SERVERS} \
--key-file ${var.private_key_file} \
--extra-vars "\
aws_access_key=${var.access_key}
aws_secret_key=${var.secret_key}
image_s3_bucket=snaps-ci
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
local_public_key='${aws_key_pair.snaps-boot-pk.public_key}'
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
proxy_host=${var.build_ip_prfx}.1
proxy_port=${var.proxy_port}
"\
EOT
  }
}

###### STOP HERE IF ONLY WANT TO BUILD AN IMAGE ######
# Wait for a couple minutes for the build server to properly initialize
# TODO/FIXME - need a better means to ensure subsequent playbooks will not fail
resource "null_resource" "snaps-boot-build-server-soak" {
  depends_on = [null_resource.snaps-boot-server-setup]

  # Install KVM dependencies
  provisioner "local-exec" {
    command = 'sleep 120'
  }
}

###### BEGIN HERE IF ONLY WANT TO RUN CI AGAINST ABOVE IMAGE ######

# Call ansible scripts to run snaps-boot
resource "null_resource" "snaps-boot-src-setup" {
  depends_on = [null_resource.snaps-boot-build-server-soak]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${var.build_ip_suffix}, \
${var.SETUP_SRC} \
--key-file ${local.remote_priv_key_file} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${var.build_ip_suffix} 22'" \
--extra-vars " \
src_copy_dir=${var.src_copy_dir}
proxy_host=${var.build_ip_prfx}.1
proxy_port=${var.proxy_port}
"\
EOT
  }
}

# Call ansible scripts to run snaps-boot
resource "null_resource" "snaps-boot-drp-setup" {
  depends_on = [null_resource.snaps-boot-src-setup]
//  depends_on = [null_resource.snaps-boot-kvm-setup]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${var.build_ip_suffix}, \
${var.SETUP_DRP} \
--key-file ${local.remote_priv_key_file} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${var.build_ip_suffix} 22'" \
--extra-vars "\
nameserver=${var.build_ip_prfx}.1
src_copy_dir=${var.src_copy_dir}
post_script_file=${var.post_script_file}
priv_ip_prfx=${var.priv_ip_prfx}
admin_ip_prfx=${var.admin_ip_prfx}
pub_ip_prfx=${var.pub_ip_prfx}
ip_suffix_1=${var.node_1_suffix}
ip_suffix_2=${var.node_2_suffix}
ip_suffix_3=${var.node_3_suffix}
priv_mac_1=${var.node_1_mac_1}
priv_mac_2=${var.node_2_mac_1}
priv_mac_3=${var.node_3_mac_1}
broadcast_addr=${var.priv_ip_prfx}.255
domain_name=cablelabs.com
dns_addr=8.8.8.8
listen_iface=ens3
max_lease=7200
netmask=255.255.255.0
router_ip=${var.priv_ip_prfx}.100 ${var.priv_ip_prfx}.254
build_ip_suffix=${var.build_ip_suffix}
http_proxy_port=${var.ngcacher_proxy_port}
priv_iface=ens3
admin_iface=ens8
pub_iface=ens9
pxe_pass=${var.pxe_pass}
hosts_yaml_path=${var.hosts_yaml_path}
org_proxy=${var.build_ip_prfx}.1:${var.proxy_port}
"\
EOT
  }
}

resource "null_resource" "snaps-boot-nodes-power-cycle" {
  depends_on = [null_resource.snaps-boot-drp-setup]
  provisioner "remote-exec" {
    inline = [
      "sudo virsh reset pxe-node-1",
      "sudo virsh reset pxe-node-2",
      "sudo virsh reset pxe-node-3",
    ]
  }
  connection {
    host = aws_spot_instance_request.snaps-boot-host.public_ip
    type     = "ssh"
    user     = var.sudo_user
    private_key = file(var.private_key_file)
  }
}

# Validate private interface is active
resource "null_resource" "snaps-boot-verify-priv-intfs" {
  depends_on = [null_resource.snaps-boot-nodes-power-cycle]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${var.build_ip_suffix}, \
${var.VERIFY_INTFS} \
--key-file ${local.remote_priv_key_file} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${var.build_ip_suffix} 22'" \
--extra-vars "{
'username': 'root',
'host_ips': ['${var.priv_ip_prfx}.${var.node_1_suffix}',
             '${var.priv_ip_prfx}.${var.node_2_suffix}',
             '${var.priv_ip_prfx}.${var.node_3_suffix}',
            ],
'timeout': '${var.initial_boot_timeout}',
}"\
EOT
  }
}

# Configure NICs
resource "null_resource" "snaps-boot-config-intf" {
  depends_on = [null_resource.snaps-boot-verify-priv-intfs]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${var.build_ip_suffix}, \
${var.CONFIG_INTFS} \
--key-file ${local.remote_priv_key_file} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${var.build_ip_suffix} 22'" \
--extra-vars "\
snaps_boot_dir=${var.src_copy_dir}/snaps-boot
hosts_yaml_path=${var.hosts_yaml_path}
"\
EOT
  }
}

# Validate private interface is active
resource "null_resource" "snaps-boot-verify-admin-priv-intfs" {
  depends_on = [null_resource.snaps-boot-config-intf]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${var.build_ip_suffix}, \
${var.VERIFY_INTFS} \
--key-file ${local.remote_priv_key_file} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${var.build_ip_suffix} 22'" \
--extra-vars "{
'username': 'root',
'host_ips': ['${var.admin_ip_prfx}.${var.node_1_suffix}',
              '${var.admin_ip_prfx}.${var.node_2_suffix}',
              '${var.admin_ip_prfx}.${var.node_3_suffix}',
              '${var.pub_ip_prfx}.${var.node_1_suffix}',
              '${var.pub_ip_prfx}.${var.node_2_suffix}',
              '${var.pub_ip_prfx}.${var.node_3_suffix}',
            ],
'timeout': '${var.std_boot_timeout}',
}"\
EOT
  }
}

# Validate private interface is active
resource "null_resource" "snaps-boot-verify-apt-proxy-node-1" {
  depends_on = [null_resource.snaps-boot-verify-admin-priv-intfs]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${var.build_ip_suffix}, \
${var.VERIFY_APT_PROXY} \
--key-file ${local.remote_priv_key_file} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${var.build_ip_suffix} 22'" \
--extra-vars "{
'username': 'root',
'ip_addr': '${var.priv_ip_prfx}.${var.node_1_suffix}',
}"\
EOT
  }
}
