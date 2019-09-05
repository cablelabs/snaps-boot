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

# Azure Credentials
//provider "azurerm" {
//  subscription_id = var.subscription_id
//  client_id = var.client_id
//  client_secret = var.client_secret
//  tenant_id = var.tenant_id
//  environment = "public"
//}

resource "azurerm_resource_group" "snaps-boot" {
  location = var.location
  name = "snaps-boot-res-grp-${var.build_id}"
}

resource "azurerm_virtual_network" "snaps-boot-net" {
  name = "snaps-boot-net-${var.build_id}"
  address_space = ["10.1.0.0/16"]
  location = azurerm_resource_group.snaps-boot.location
  resource_group_name = azurerm_resource_group.snaps-boot.name
}

resource "azurerm_subnet" "snaps-boot-subnet" {
  name = "snaps-boot-subnet-${var.build_id}"
  virtual_network_name = azurerm_virtual_network.snaps-boot-net.name
  resource_group_name = azurerm_resource_group.snaps-boot.name
  address_prefix = "10.1.0.0/24"
}

resource "azurerm_public_ip" "snaps-boot-pub-ip" {
  name = "snaps-boot-${var.build_id}"
  location = azurerm_resource_group.snaps-boot.location
  resource_group_name = azurerm_resource_group.snaps-boot.name
  allocation_method = "Static"
}

resource "azurerm_network_interface" "snaps-boot-nic" {
  name = "snaps-boot-${var.build_id}-nic"
  location = azurerm_resource_group.snaps-boot.location
  resource_group_name = azurerm_resource_group.snaps-boot.name

  ip_configuration {
    name                          = "configuration"
    subnet_id                     = azurerm_subnet.snaps-boot-subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.snaps-boot-pub-ip.id
  }
}

resource "azurerm_virtual_machine" "snaps-boot-host" {
  name = "snaps-boot-host-${var.build_id}"

  delete_os_disk_on_termination = true
  delete_data_disks_on_termination = true

  location = azurerm_resource_group.snaps-boot.location
  resource_group_name = azurerm_resource_group.snaps-boot.name
  network_interface_ids = [azurerm_network_interface.snaps-boot-nic.id]
  vm_size = var.vm_size

  os_profile {
    admin_username = "ubuntu"
    admin_password = "Cable123"
    computer_name = "snaps-boot-host"
  }

  os_profile_linux_config {
    disable_password_authentication = false
    ssh_keys {
      key_data = file(var.public_key_file)
      path = "/home/${var.sudo_user}/.ssh/authorized_keys"
    }
  }

  storage_image_reference {
    id = "/subscriptions/ffc5d93a-8a85-4c42-8c33-7d0d762e852d/resourceGroups/snaps-boot-ci/providers/Microsoft.Compute/galleries/snaps_boot_gallery/images/snaps_boot_img/versions/0.0.2"
  }

  storage_os_disk {
    name = "snaps-boot-disk-${var.build_id}"
    disk_size_gb = var.volume_size
    caching = "ReadWrite"
    create_option = "FromImage"
    managed_disk_type = "Standard_LRS"
  }

  tags = {
    Name = "snaps-boot-build-${var.build_id}"
  }

  # Used to ensure host is really up before attempting to apply ansible playbooks
  provisioner "remote-exec" {
    inline = [
      "echo 'hello ${var.build_id}' /etc/motd"
    ]
  }

  # Remote connection info for remote-exec
  connection {
    host = azurerm_public_ip.snaps-boot-pub-ip.ip_address
    type     = "ssh"
    user     = var.sudo_user
    private_key = file(var.private_key_file)
    timeout = "15m"
  }
}
