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

# Call ansible scripts to setup and run snaps-boot
resource "null_resource" "snaps-boot-build" {
  provisioner "local-exec" {
    command = "chmod 600 ${var.private_key_file}"
  }

  # Setup KVM on the VM to create VMs on it for testing snaps-boot
  provisioner "local-exec" {
    command = <<EOT
${var.ANSIBLE_CMD} -u ${var.sudo_user} \
-i ${aws_instance.snaps-boot-build.public_ip}, \
${var.SETUP_KVM_PB} \
--key-file ${var.private_key_file} \
--extra-vars "\
priv_ip_prfx=10.0.1 \
admin_ip_prfx=10.0.2 \
pub_ip_prfx=10.0.3
"\
EOT
  }

}
