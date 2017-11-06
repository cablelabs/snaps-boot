# Installation

This document serves as a guide specifying the steps and configuration required for OS provisioning of bare metal machines via SNAPS-PXE. It does not provide implementation level details.

This document is to be used by development team, validation and network test teams.

## 1 Introduction

### 1.1 Terms and Conventions

The terms and typographical conventions used in this document are listed and explained in below table.

| Convention | Usage |
| ---------- | ----- |
| Host Machines | Machines to be used for Openstack deployment. Openstack node controller, compute, storage and network node will be deployed on these machines. |
| Configuration node | Machine running installation scripts, PXE, DHCP, TFTP etc. |

### 1.2 Acronyms

The acronyms expanded in below are fundamental to the information in this document.

| Acronym | Explanation |
| ------- | ----------- |
| SNAPS | SDN/NFV Application Platform/Stack |
| PXE | Preboot Execution Environment |
| IP | Internet Protocol |
| COTS | Commercial Off The Shelf |
| OS | OpenStack |
| DHCP | Dynamic Host Configuration Protocol |
| TFTP | Trivial FTP |

### 1.3 References

[1] Openstack Installation guide: https://docs.openstack.org/newton/install-guide-ubuntu/

## 2 Environment Prerequisites

### 2.1 Hardware Requirements

The current release of SNAPS-PXE is tested on the following platform.

**Compute Node**

| Hardware Required | Description | Configuration |
| ----------------- | ----------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | COTS servers. | 16GB RAM, 80+ GB Hard disk with 3 network interfaces. Server should be network boot Enabled and IPMI capable. |

**Controller Node**

| Hardware Required | Description | Configuration |
| ----------------- | ----------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | COTS servers. | 16GB RAM, 80+ GB Hard disk with 3 network interfaces. Server should be network boot Enabled and IPMI capable. |

**Configuration Node**

| Hardware Required | Description | Configuration |
| ----------------- | ----------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | COTS servers. | 1 6GB RAM, 80+ GB Hard disk with 1 network interface. |

### 2.2 Software Requirements

| Category | Software version |
| -------- | ---------------- |
| Operating System |  Ubuntu 16. |
| Scripting | Python 2.6.X |
| Framework |  Ansible 2.3.0. |
| Openstack |  Newton |

### 2.3 Additional Requirements

- Machine running SNAPS-PXE should have Ubuntu 16.04 Xenial as host OS and should have internet access.
- All host machines should have identical interface names and should have at least 2 interfaces (one for management and one for data).
- All host machines are connected to configuration node (machine running SNAPS-PXE) and have Internet access connectivity via data interface.

> Note: Configuration node should have http/https and ftp proxy if node is behind corporate firewall. Set the http/https proxy for apt.

## 3 Configuration

### 3.1 hosts.yaml

Configuration file used for hardware provisioning. Options defined here are used by deployment layer to discover and net boot host machines, allocate IP addresses, set proxies and install operating system on these machines.

#### DHCP:

Configurations defined here are used to discover host machines and dynamically allocate IPs to them.

Deployment layer installs a DHCP server on the configuration node and configures it to allocate IPs to host machine. This DHCP server can be configured to support multiple subnets. User is required to define DHCP parameters for each subnet and fixed IPs to be allocated from the subnets.

User is required to add a subnet section for each network being used in data centre. It is mandatory to define management subnet here; the other subnets are optional and are required only if user wishes to allocate static IPs from those subnets.

> Note: **For static IP allocation define section ‘STATIC’**

Configuration parameter defined in this section are explained below.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| address | N | Subnet address |
| bind_host | N | This section defines group of mac and ip address. User is required to create one such group for each host machine. The ip addresses defined here are allocated by the SNAPS-PXE during OS provisioning. The ip addresses defined here should be from the subnet defined by parameter ‘address’. |
| broadcast-address | Y | Broadcast address for the subnet |
| default-lease | N | Lease time (in seconds) to be used by DHCP server on configuration node. |
| dn | N | Domain name of configuration node. |
| dns | N | IP of domain name server. |
| listen_iface | N | Name of interface to which DHCP server will bind for IP requests. |
| max-lease | N | Maximum lease time (in seconds) for DHCP server running on configuration node. |
| Name | N | Human readable name for this subnet. |
| netmask | N | Netmask of the subnet. |
| range | N | IP range to be used on this subnet. User is required to define a string of first and last ip address, see example below "172.16.109.210 172.16.109.224" |
| routers | N | IP of external router (gateway ip). |
| Type | N | Type of network this subnet will serve. Possible values are: **management**, **ipmi** (to be used only if user wants to modify IP address allocated to IPMI interfaces), **data**, **external**. |

> Note: For optional parameters, use null value **“”** if not required.

#### PROXY:

Configuration node and all other host machines requires internet connectivity to download open ware tools (python, Ansible etc.) and OpenStack services. User is required to set FTP, HTTP and HTTPs proxies on these machines if internet access is restricted by firewall.

Configuration parameter defined in this section are explained below.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| ftp_proxy | Y | Proxy to be used for FTP. |
| http_proxy | Y | Proxy to be used for HTTP traffic. |
| https_proxy | Y | Proxy to be used for HTTPS traffic. |

> Note: If proxy configuration is not required use null value **“”** for each of the parameters

#### PXE:

Configuration parameter defined here are used by PXE server.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| serverIp | N | IP of configuration node where PXE server is running. |
| user | N | User of PXE server (User of configuration node). |
| password | N | Password for user of PXE server. |

#### STATIC:

SNAPS-PXE can be configured to allocate static IPs to host machines. This section has sub-section for each host machine. User is required to specify all the interfaces and IPs to be assigned to those interfaces.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| access_ip | N | IP of the interface on management subnet (this is the IP allocated by SNAPS-PXE DHCP configuration to this machine). |
| name | N | OpenStack node type for this machine. Human readable values just for identification. For example: Controller, Compute1, Compute2 etc. |
| interfaces | N | This section should be defined for each interface to be provisioned for static IP allocation. Each interface is defined by the attributes that follow. |
| address | N | IP address to be allocated to the interface. |
| dn | Y | Domain name. |
| dns | Y | IP of domain name server. |
| gateway | N | IP of the gateway to be used for this interface. |
| iface | N | Name of the interface. |
| name | N | Human readable name for this subnet. |
| netmask | N | Netmask of the subnet (IP is allocated from this subnet). |
| type | N | Type of network this subnet will serve. Possible values are: **management**, **ipmi**, **tenant**, **data**. |

> Note: For optional parameters, use null value **“”** if not required. For **‘data’** interface it is mandatory to define **‘dn’** and **‘dns’**.

#### BMC:

Parameters defined here are used by SNAPS-PXE IPMI agents to communicate with host machines over IPMI interface. User is required to provide this information of each host machine.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| user | N | Username to be used for IPMI. |
| password | N | Password to be used for IPMI. |
| ip | N | IP assigned to IPMI interface of the machine. |
| mac | N | Mac address of the IPMI interface of the machine. |

#### TFTP:

This section defines parameters to specify the host OS image and SEED file to be used for remote booting of host machines.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| os | N | ISO of OS image to be installed on host machines. |
| seed | N | Seed file to be used for host OS installation. |
| timezone | N | Time zone configuration for host machines. |
| user | N | Default user for all host machines. SNAPS-PXE creates this user. |
| password | N | Password for the default user created by SNAPS-PXE. |
| fullname | Y | Description of user created by SNAPS-PXE. |

#### CPUCORE:

This section is used to define parameters for isolating CPUs (Host vs Guest OS) and for creating persistent huge pages. SNAPS-PXE reads these parameters and make appropriate changes in OS grub file.

Configuration parameter defined in this section are explained below.

| Parameter | Optionality | Description |
| --------- | ----------- | ----------- |
| ip | Y | IP of host machine. |
| isolcpus | Y | Processor ids to be isolated for guest OS use. |
| hugepagesz | Y | Size of memory pages (2M, 1 G etc.). |
| hugepages | Y | Number of huge pages. |

CPUCORE section is an optional section. User should define these set of parameters for each host machine where CPU isolation and persistent huge memory pages are to be defined.

## 4 Installation Steps

### 4.1 OS Provisioning with 2 or more NICs

#### Step 1

Clone/FTP [SNAPS-PXE repo](https://github.com/cablelabs/snaps-pxe) on configuration node. All operations of configuration server expect the user should be explicitly switched (using `su root`) to the root user.

In addition, user needs to download `ubuntu16.04 server image` from internet and need to place it in folder `~/snaps-pxe/snaps-pxe/packages/images/`. Use this download link for ISO: http://releases.ubuntu.com/16.04/ubuntu-16.04.3-server-amd64.iso then select and click on “64 - bit PC (AMD64) server install image”.

#### Step 2

Go to directory `~/snaps-pxe/snaps-pxe/conf/pxe_cluster`.

Modify file `hosts.yaml` for provisioning of OS (Operating System) on cloud cluster host machines
(controller node, compute nodes). Modify this file according to your set up environment only.

#### Step 3

Go to directory `~/snaps-pxe/snaps-pxe/`

Change execution permissions for `PreRequisite.sh`. Run `PreRequisite.sh` as shown below:

```
./PreRequisite.sh
```

#### Step 4

Steps to configure PXE and DHCP server.

Go to directory `~/snaps-pxe/snaps-pxe/`.

Run `iaas_launch.py` as shown below:

```
root@conf-server# python iaas_launch.py -f conf/pxe_cluster/hosts.yaml -p
```

#### Step 5

Manually verify DHCP server is running or not, using below given command:

```
sudo systemctl status isc-dhcp-sever
```

State should be active running.

Manually verify tftp-hpa service is running or not, using below given command:

```
sudo systemctl status tftpd-hpa
```

State should be active running.

Manually verify apache2 service is running or not, using below given command:

```
sudo systemctl status apache
```

State should be active running.

#### Step 6

Run `iaas_launch.py` as shown below:

```
root@conf-server# python iaas_launch.py -f conf/pxe_cluster/hosts.yaml -b
```

This will boot host machines (controller/compute nodes), select NIC Controller (PXE client
enabled) to use network booting.

Your OS provisioning will start and will get completed in 20 minutes.

#### Step 7

Execute this step only if static IPs to be assigned to host machines.

Run `iaas_launch.py` as shown below:
```
root@conf-server# python iaas_launch.py -f conf/pxe_cluster/hosts.yaml -s
```

#### Step 8

Execute this step either for defining large memory pages or for isolating CPUs between host and guest OS.

```
root@conf-server# python iaas_launch.py -f conf/pxe_cluster/hosts.yaml -i
```

> Note: This step is optional and should be executed only if CPU isolation or large memory page provisioning is required.

### 4.2 OS Provisioning with single NIC

The process for OS provisioning with a single NIC is currently TBD.

## 5 Clean-up and Troubleshooting

### 5.1 Roll-back Isolated CPUs and Huge Pages

```
sudo python iaas_launch.py -f conf/pxe_cluster/hosts.yaml -ic
```

This will modify grub file on all host machines to remove isolated cpu and huge page configuration and will boot the machine to default configuration.

### 5.2 Roll-back Static IP Configuration and Change Default Routes Back to Management Interface

```
sudo python iaas_launch.py -f conf/pxe_cluster/hosts.yaml - sc
```

This will modify etc/network/interfaces file to remove static entries of the interfaces and will change back default route to management interface.

### 5.3 Roll-back of SNAPS-PXE Installation

```
sudo python iaas_launch.py - conf/pxe_cluster/hosts.yaml - pc
```

This will stop DHCP, PXE and TFTP services on configuration node.
