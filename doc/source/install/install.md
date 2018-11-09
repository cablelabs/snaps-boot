# Installation

This document serves as a guide specifying the steps and configuration
required for OS provisioning of bare metal machines via SNAPS-Boot.
It does not provide implementation level details.

This document is to be used by development team, validation and network
test teams.

## 1 Introduction

### 1.1 Terms and Conventions

The terms and typographical conventions used in this document are
listed and explained in below table.
<br><br>

| Convention | Usage |
| ---------- | ----- |
| Host Machines | Machines to be used for Openstack deployment. Openstack node controller, compute, storage and network node will be deployed on these machines. |
| Build Server | Machine running installation scripts, and hosting PXE, DHCP, TFTP services. |

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
| UEFI | Unified Extensible Firmware Interface |
| BIOS | Basic Input Output System |
| DRP | Digital Rebar Provision |

### 1.3 References

1. OpenStack Installation Guide: https://docs.openstack.org/newton/install-guide-ubuntu/
2. UEFI PXE Netboot/Install Procedure: https://wiki.ubuntu.com/UEFI/PXE-netboot-install
3. Digital Rebar Provision Quick Start: https://provision.readthedocs.io/en/stable/doc/quickstart.html#rs-quickstart

## 2 Environment Prerequisites

### 2.1 Hardware Requirements

The hardware requirements are based on the OPNFV Pharos Specification
https://wiki.opnfv.org/display/pharos/Pharos+Specification.
Areas where SNAPS-Boot differs from Pharos are noted below.
The current release of SNAPS-Boot is tested on the following platform.

**Compute Node**

| Hardware Required | Configuration |
| ----------------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | 16GB RAM, 80+ GB Hard disk with 3 network interfaces. Server should be network boot Enabled and IPMI capable. |

**Controller Node**

| Hardware Required | Configuration |
| ----------------- |  ------------- |
| Server machine with 64bit Intel AMD architecture. | 16GB RAM, 80+ GB Hard disk with 3 network interfaces. Server should be network boot Enabled and IPMI capable. |

**Build Server**

| Hardware Required | Configuration |
| ----------------- | ------------- |
| Server machine with 64bit Intel AMD architecture. | 16GB RAM, 80+ GB Hard disk with 1 network interface. |

### 2.2 Software Requirements

| Category | Software version |
| -------- | ---------------- |
| Operating System |  Ubuntu 16.04 |
| Scripting | Python 2.7.X |
| Framework |  Ansible 2.3.3.0 |

### 2.3 Network configuration

- All host machines must have identical network interfaces.
- 3 NICs per server are recommended, but only two are required.
 - When only two physical networks are configured, one is used for PXE
deployments and the other is used for VNF traffic.
 - When three physical networks are used, the external and tenant
 traffic are separated.
- Each NIC needs to be on a separate VLAN.
- The first NIC is the management network.  This is used to install Linux
on the host machines.
- All host machines are connected to Build Server (machine
running SNAPS-Boot) and have Internet access connectivity via data
interface.

> Note: Build Server should have http/https and ftp proxy if
node is behind corporate firewall. Set the http/https proxy for apt.

### 2.4 Build Server Setup

The Build Server is where you run SNAPS-Boot. You will need to install
Ubuntu 16.04 Xenial as host OS. This host needs to be able to reach the Internet
to download the software.

1. Install Ubuntu on the Build Server
2. Download SNAPS-boot from GitHub
```
git clone https://github.com/cablelabs/snaps-boot.git
```

3. Install

```
sudo apt install python-pip
sudo pip install -r snaps-boot/requirements-git.txt
sudo pip install -e snaps-boot/
```

>:warning: Note:  If you use git, make sure not to push your changes back to the repository.
## 3 Configuration

### 3.1 snaps-boot Configuration

Configuration file used for hardware provisioning. Options defined here
are used by deployment layer to discover and net boot host machines,
allocate IP addresses, set proxies and install operating system on
these machines.

Use the doc/conf/hosts.yaml file as a template for configuring your
environment for use as your -f argument to iaas_launch.py. (note: the
file does not need to be called hosts.yaml or reside in any particular
directory)

#### DHCP:

Configurations defined here are used to discover host machines and
dynamically allocate IPs to them.

Deployment layer installs a DHCP server on the Build Server and
configures it to allocate IPs to host machine. This DHCP server can be
configured to support multiple subnets. For each subnet, DHCP parameters
and fixed IPs must be defined.

The DHCP section of the hosts.yaml file is only used for the management 
network to install the servers. After the servers are installed the networking 
information in the hosts section can be configured statically on all interfaces 
including the management network.

The management and data networks are mandatory.  The tenant network is recommended, but is optional.

> Note: **For static IP allocation define section ‘STATIC’**

Configuration parameters for the subnet section are explained below.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| subnet | Y | Subnet address e.g. 10.10.10.0 |
| dn | Y | Domain name of Build Server. |
| dns | Y | IP of domain name server. |
| netmask | Y | Netmask of the subnet. |
| range | Y | IP range to be used on this subnet. User is required to define a string of first and last ip address, see example below "172.16.109.210 172.16.109.224" |
| router | Y | IP of external router (gateway ip). |

> Note: For optional parameters, use null value **“”** if not required.

#### PROXY:

Build Server and all other host machines requires internet
connectivity to download open source tools (python, Ansible etc.) and
OpenStack services. User is required to set FTP, HTTP, HTTPs and NG-CACHER  proxies
on these machines if internet access is restricted by firewall.

Configuration parameter defined in this section are explained below.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| ftp_proxy | N | Proxy to be used for FTP. |
| http_proxy | N | Proxy to be used for HTTP traffic. |
| https_proxy | N | Proxy to be used for HTTPS traffic. |
| ngcacher_proxy | N | Proxy should be set in case the servers are behind corporate firewalls. |


> Note: If proxy configuration is not required use null value **“”**
for each of the parameters.  Do not remove the line from the file.

#### PXE:

Configuration parameter defined here are used by PXE server, usually the Build Server.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| server_ip | Y | IP of Build Server where PXE server is running. |
| user | Y | User of PXE server (User of Build Server). |
| password | Y | Password for user of PXE server. |

#### STATIC:

SNAPS-Boot can be configured to allocate static IPs to host machines. This section has sub-section for each host machine. User is required to specify all the interfaces and IPs to be assigned to those interfaces.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| access_ip | Y | IP of the interface on management subnet (this is the IP allocated by SNAPS-Boot DHCP configuration to this machine). |
| name | Y | OpenStack node type for this machine. Human readable values just for identification. For example: Controller, Compute1, Compute2 etc. |
| interfaces | Y | This section should be defined for each interface to be provisioned for static IP allocation. Each interface is defined by the attributes that follow. |
| address | Y | IP address to be allocated to the interface. |
| dn | N | Domain name. |
| dns | N | IP of domain name server. |
| gateway | Y | IP of the gateway to be used for this interface. |
| iface | Y | Name of the interface. |
| name | Y | Human readable name for this subnet. |
| netmask | Y | Netmask of the subnet (IP is allocated from this subnet). |
| type | Y | Type of network this subnet will serve. Possible values are: **management**, **ipmi**, **tenant**, **data**. |

> :warning: Note: For all **‘data’** interfaces it is mandatory to define **‘dn’** and **‘dns’**.

> For optional parameters, use null value **“”** if not required. 


#### BMC:

Parameters defined here are used by SNAPS-Boot IPMI agents to communicate with host machines over IPMI interface. User is required to provide this information of each host machine.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| user | Y | Username to be used for IPMI. |
| password | Y | Password to be used for IPMI. |
| ip | Y | IP assigned to IPMI interface of the machine. |
| mac | Y | Mac address of the IPMI interface of the machine. |

#### TFTP:

This section defines parameters used in preseed configuration to automate Linux OS installation.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| pxe_server_configuration |  | Details of OS to be used in PXE based installation.  |

##### Ubuntu
| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| ubuntu |  | Details of Ubuntu OS. |
| password | Y | Password for the default user created by SNAPS-Boot. |
| timezone | Y | Time zone configuration for host machines. |
| user | Y | Default user for all host machines. SNAPS-Boot creates this user. |
| fullname | Y | Description of user created by SNAPS-Boot. |
| boot_disk | Y | Disk name where OS is installed, e.g., sda |

##### CentOS
| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| centos |  | Details of Centos OS. |
| password | Y | Password for the default user created by SNAPS-Boot. |
| timezone | Y | Time zone configuration for host machines. |
| user | Y | Default user for all host machines. SNAPS-Boot creates this user. |
| fullname | Y | Description of user created by SNAPS-Boot. |
| boot_disk | Y | Disk name where OS is installed, e.g., sda |

> Note: User has to give details of at least one OS(either Ubuntu OS or Centos OS or Both) as per the PXE requirement.

#### CPUCORE:

This section is used to define parameters for isolating CPUs (Host vs
Guest OS) and for creating persistent huge pages. SNAPS-Boot reads these
parameters and make appropriate changes in OS grub file.

Configuration parameter defined in this section are explained below.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| ip | N | IP of host machine. |
| isolcpus | N | Processor ids to be isolated for guest OS use. |
| hugepagesz | N | Size of memory pages e.g. 2M, 1G (M=megabytes, G=gigabytes). |
| hugepages | N | Number of huge pages. |

CPUCORE section is an optional section. User should define these set of
parameters for each host machine where CPU isolation and persistent huge
memory pages are to be defined.

## 4 Installation Steps

### 4.1 Server Provisioning

Note:  All of the following steps are executed within the root directory of your 
snaps-boot project.  This will usually be snaps-boot/, so it assumed you are in this 
directory. 

#### Step 1 - Build host setup
Setup your Python 2.7 runtime (script example below is for Ubuntu)
```
sudo apt install python
sudo apt install python-pip
```

#### Step 2 - Obtaining the snaps-boot source
Clone this git repository and install into your Python 2.7 runtime
```
git clone https://github.com/cablelabs/snaps-boot
sudo pip install -r snaps-boot/requirements-git.txt
sudo pip install -e snaps-boot/
```

#### Step 3 - Configure your rack
Go to root directory of the project (e.g. `snaps-boot`)

Create a configuration file based on `doc/conf/hosts.yaml` for provisioning
of the Operating System on these nodes

Note:
For provisioning only ubuntu PXE Server, Keep ubuntu list under TFTP section in hosts.yaml.
For provisioning only centos PXE Server, Keep centos list under TFTP section in hosts.yaml.
For provisioning both, Keep both ubuntu and centos lists under TFTP section in hosts.yaml.
      
#### Step 4 - Deploy

Steps to configure PXE and DHCP server.

Run `iaas_launch.py` as shown below as a passwordless sudo user:

```
python {git dir}/snaps-boot/iaas_launch.py -f {location of your configuration} -p
```

#### Step 7 - Static NIC Configuration
Go to root directory of the project (e.g. `snaps-boot`)

Execute this step only if static IPs to be assigned to host machines.

Run `iaas_launch.py` as shown below:
```
python {git dir}/snaps-boot/iaas_launch.py -f {location of your configuration} -s
```
>:warning: This step will reboot each target server when it is done.  
Wait a few minutes then ping and/or ssh each management server to verify  
it is back up. 

#### Step 8
Go to root directory of the project (e.g. `snaps-boot`)

Execute this step either for defining large memory pages or for
isolating CPUs between host and guest OS.

```
python {git dir}/snaps-boot/iaas_launch.py -f {location of your configuration} -i
```

> Note: This step is optional and should be executed only if CPU
isolation or large memory page provisioning is required.

## 5 Clean-up and Troubleshooting

### 5.1 Roll-back Isolated CPUs and Huge Pages

```
python {git dir}/snaps-boot/iaas_launch.py -f {location of your configuration} -ic
```

This will modify grub file on all host machines to remove isolated cpu
and huge page configuration and will boot the machine to default
configuration.

### 5.2 Roll-back Static IP Configuration and Change Default Routes
Back to Management Interface

```
python {git dir}/snaps-boot/iaas_launch.py -f {location of your configuration} -sc
```

This will modify etc/network/interfaces file to remove static entries of the interfaces and will change back default route to management interface.

### 5.3 Roll-back of SNAPS-Boot Installation

```
python {git dir}/snaps-boot/iaas_launch.py -f {location of your configuration} -pc
```

This will stop DHCP, PXE and TFTP services on Build Server.
