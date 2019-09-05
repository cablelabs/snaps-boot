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

# Call ansible scripts to run snaps-hyperbuild
resource "null_resource" "snaps-hyperbuild-wait-for-build" {
  depends_on = [null_resource.snaps-boot-pk-setup]

  # Setup KVM on the VM to create VMs on it for testing snaps-hyperbuild
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_spot_instance_request.snaps-boot-host.public_ip}, \
${var.WAIT_FOR_BUILD} \
--key-file="${var.private_key_file}" \
--extra-vars " \
host=${var.build_ip_prfx}.${var.build_ip_suffix}
pause_time=5
"\
EOT
  }
}

resource "random_integer" "snaps-boot-ip-prfx" {
  min = 101
  max = 254
}

# Add local key to build server
resource "null_resource" "snaps-boot-inject-pub-key-to-build" {
  depends_on = [null_resource.snaps-hyperbuild-wait-for-build]
  provisioner "remote-exec" {
    inline = [
      "ssh -o StrictHostKeyChecking=no ${var.sudo_user}@${var.build_ip_prfx}.${var.build_ip_suffix} 'rm -f ~/.ssh/known_hosts'",
      "ssh -o StrictHostKeyChecking=no ${var.sudo_user}@${var.build_ip_prfx}.${var.build_ip_suffix} 'touch ~/.ssh/authorized_keys'",
      "ssh -o StrictHostKeyChecking=no ${var.sudo_user}@${var.build_ip_prfx}.${var.build_ip_suffix} 'echo ${aws_key_pair.snaps-boot-pk.public_key} >> /home/${var.sudo_user}/.ssh/authorized_keys'",
      "ssh -o StrictHostKeyChecking=no ${var.sudo_user}@${var.build_ip_prfx}.${var.build_ip_suffix} 'chmod 600 ~/.ssh/authorized_keys'",
      "ssh -o StrictHostKeyChecking=no ${var.sudo_user}@${var.build_ip_prfx}.${var.build_ip_suffix} 'cp ~/.ssh/authorized_keys ~/.ssh/authorized_keys.bak'",
      "ssh -o StrictHostKeyChecking=no ${var.sudo_user}@${var.build_ip_prfx}.${var.build_ip_suffix} 'sudo ip addr add ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result}/24 dev ens3'",
    ]
  }
  connection {
    host = aws_spot_instance_request.snaps-boot-host.public_ip
    type = "ssh"
    user = var.sudo_user
    private_key = file(var.private_key_file)
  }
}

# Call ansible scripts to run snaps-boot
resource "null_resource" "snaps-boot-src-setup" {
  depends_on = [null_resource.snaps-boot-inject-pub-key-to-build]

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result}, \
${var.SETUP_SRC} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result} 22'" \
--key-file="${var.private_key_file}" \
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

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result}, \
${var.SETUP_DRP} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result} 22'" \
--key-file="${var.private_key_file}" \
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
bcast_addr=${var.priv_ip_prfx}.255
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
      "sudo virsh reset ${var.node_1_name}",
      "sudo virsh reset ${var.node_2_name}",
      "sudo virsh reset ${var.node_3_name}",
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
-i ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result}, \
${var.VERIFY_INTFS} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result} 22'" \
--key-file="${var.private_key_file}" \
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
-i ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result}, \
${var.CONFIG_INTFS} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result} 22'" \
--key-file="${var.private_key_file}" \
--extra-vars "\
snaps_boot_dir=${var.src_copy_dir}/snaps-boot
hosts_yaml_path=${var.hosts_yaml_path}
check_file=${var.VERIFY_INTFS_CHECK_FILE}
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
-i ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result}, \
${var.VERIFY_INTFS} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result} 22'" \
--key-file="${var.private_key_file}" \
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
-i ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result}, \
${var.VERIFY_APT_PROXY} \
--ssh-common-args="-o ProxyCommand='ssh ${var.sudo_user}@${aws_spot_instance_request.snaps-boot-host.public_ip} nc ${var.build_ip_prfx}.${random_integer.snaps-boot-ip-prfx.result} 22'" \
--key-file="${var.private_key_file}" \
--extra-vars "{
'username': 'root',
'ip_addr': '${var.priv_ip_prfx}.${var.node_1_suffix}',
}"\
EOT
  }
}
