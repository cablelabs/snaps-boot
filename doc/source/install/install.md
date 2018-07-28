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

### 1.3 References

1. OpenStack Installation Guide: https://docs.openstack.org/newton/install-guide-ubuntu/
2. UEFI PXE Netboot/Install Procedure: https://wiki.ubuntu.com/UEFI/PXE-netboot-install

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
| Scripting | Python 2.6.X |
| Framework |  Ansible 2.3.0. |

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
wget https://github.com/cablelabs/snaps-boot/archive/master.zip
```
3. Extract the files
```
unzip master.zip
```

> Note: Git can also be used to clone the repository.

```
git clone https://github.com/cablelabs/snaps-boot.git
```

>:warning: Note:  If you use git, make sure not to push your changes back to the repository.
## 3 Configuration

### 3.1 conf/pxe-cluster/hosts.yaml

Save a copy of hosts.yaml before modifying it.
`cp hosts.yaml origional-hosts.yaml`

Configuration file used for hardware provisioning. Options defined here
 are used by deployment layer to discover and net boot host machines,
 allocate IP addresses, set proxies and install operating system on
  these machines.

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
| address | Y | Subnet address e.g. 10.10.10.0 |
| bind_host | Y | This section defines group of mac and ip address. One such group is required for each host machine. The ip addresses defined here are allocated by the SNAPS-Boot during OS provisioning. The ip addresses defined here should be from the subnet defined by parameter ‘address’. |
| broadcast-address | N | Broadcast address for the subnet |
| default-lease | Y | Lease time (in seconds) to be used by DHCP server on Build Server. |
| dn | Y | Domain name of Build Server. |
| dns | Y | IP of domain name server. |
| listen_iface | Y | Name of interface to which DHCP server will bind for IP requests. |
| max-lease | Y | Maximum lease time (in seconds) for DHCP server running on Build Server. |
| Name | Y | Human readable name for this subnet. |
| netmask | Y | Netmask of the subnet. |
| range | Y | IP range to be used on this subnet. User is required to define a string of first and last ip address, see example below "172.16.109.210 172.16.109.224" |
| routers | Y | IP of external router (gateway ip). |
| Type | Y | Type of network this subnet will serve. Possible values are: **management**, **ipmi** (to be used only if user wants to modify IP address allocated to IPMI interfaces), **data**, **external**. |

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
| serverIp | Y | IP of Build Server where PXE server is running. |
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

This section defines parameters to specify the host OS image and SEED file to be used for remote booting of host machines.

| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| pxe_server_configuration |  | Details of OS to be used in PXE server installation.  |

##### Ubuntu
| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| ubuntu |  | Details of Ubuntu OS. |
| os | N | ISO of ubuntu OS image to be installed on host machines. |
| password | N | Password for the default user created by SNAPS-Boot. |
| seed | N | Seed file to be used for host OS installation. |
| timezone | N | Time zone configuration for host machines. |
| user | N | Default user for all host machines. SNAPS-Boot creates this user. |
| fullname | N | Description of user created by SNAPS-Boot. |
| server_type | N | Tells the bootloader the type of the target system, UEFI or BIOS.  Defaults to BIOS. 

##### CentOS
| Parameter | Required | Description |
| --------- | ----------- | ----------- |
| centos |  | Details of Centos OS. |
| os | N | ISO of centos OS image to be installed on host machines. |
| root_password | N | Password for the root user created by SNAPS-Boot. |
| user | N | Default user for all host machines. SNAPS-Boot creates this user. |
| user_password | N | Password for the default user created by SNAPS-Boot. |
| timezone | N | Time zone configuration for host machines. |
| boot_disk | N | The device name of the boot disk (default is sda) |

>:exclamation: Note: If you installing to a UEFI system, make sure your seed file is `ubuntu-uefi-server.seed`.
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

#### Step 1

##### PXE BIOS Install
Go to root directory of the project (e.g. `snaps-boot`)

Download `ubuntu16.04` or `CentOS-7` server image from internet and need to place it
in folder `snaps-boot/packages/images/`. 
Use following download links for ISO:
##### For ubuntu
 http://releases.ubuntu.com/16.04/ubuntu-16.04.4-server-amd64.iso
##### For centos
 Download the latest "Everything ISO" from https://www.centos.org/download/

```
mkdir -p packages/images
cd packages/images
wget http://releases.ubuntu.com/16.04/ubuntu-16.04.4-server-amd64.iso
wget http://mirror.umd.edu/centos/7/isos/x86_64/CentOS-7-x86_64-Everything-1804.iso
```
Note: Please ensure that Ubuntu 16.04 server will be used to configure CentOS 7 PXE Server.

##### PXE UEFI Install
>:exclamation:CentOS is not yet supported for UEFI Installs
 
Go to root directory of the project (e.g. `snaps-boot`)

Download `grubnetx64.efi.signed` from internet and need to place it
in folder `packages/images/`.  
Use this download link:  
    http://archive.ubuntu.com/ubuntu/dists/xenial/main/uefi/grub2-amd64/current/grubnetx64.efi.signed

Download `ubuntu16.04 server image` from internet and need to place it
in folder `packages/images/`.  
Use this download link for ISO:  
    http://releases.ubuntu.com/16.04/ubuntu-16.04.4-server-amd64.iso.
    
```
mkdir -p packages/images
cd packages/images
wget http://archive.ubuntu.com/ubuntu/dists/xenial/main/uefi/grub2-amd64/current/grubnetx64.efi.signed
wget http://releases.ubuntu.com/16.04/ubuntu-16.04.4-server-amd64.iso
```

#### Step 2
Go to root directory of the project (e.g. `snaps-boot`)

Go to directory `conf/pxe_cluster`.

Modify file `hosts.yaml` for provisioning of OS (Operating System) on
cloud cluster host machines (controller node, compute nodes). Modify
this file according to your set up environment only.

Note:
For provisioning only ubuntu PXE Server, Keep ubuntu list under TFTP section in hosts.yaml.  
For provisioning only centos PXE Server, Keep centos list under TFTP section in hosts.yaml.  
For provisioning both, Keep both ubuntu and centos lists under TFTP section in hosts.yaml.
      
#### Step 3

Go to root directory of the project (e.g. `snaps-boot`)

Run `PreRequisite.sh` as shown below:

```
sudo ./scripts/PreRequisite.sh
```

If you see failures or errors, update your software, remove obsolete
packages and reboot your server.

```
sudo apt-get update
sudo apt-get upgrade
sudo apt-get auto-remove
sudo reboot
```

#### Step 4

Steps to configure PXE and DHCP server.

Go to root directory of the project (e.g. `snaps-boot`)


Run `iaas_launch.py` as shown below:

```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -p
```

Note: This updates the networking on the server and may cause your
ssh session to be terminated.

##### Step 4a
>:warning: This step is only if you require custom or proprietary drivers, such as ethernet.  If not you should skip this step. 

If your target servers require custom or proprietary drivers, you will need to provide your own initrd.gz file
for both the installer and the installation. 

For more on injecting driver modules into an initrd.gz file see

>http://www.linux-admins.net/2014/02/injecting-kernel-modules-in-initrdgz.html

Once you have a customized initrd.gz, make a backup of the existing initrd.gz

```
sudo cp <tftpdirectory>/ubuntu-installer/amd64/initrd.gz <tftpdirectory>/ubuntu-installer/amd64/initrd.gz.backup
sudo cp <www/html directory>/ubuntu/install/netboot/ubuntu-installer/amd64/initrd.gz <www/html directory>/ubuntu/install/netboot/ubuntu-installer/amd64/initrd.gz.backup
```

Now copy your initrd.gz file to each location
```
sudo cp initrd.gz <tftpdirectory>/ubuntu-installer/amd64/initrd.gz 
sudo cp initrd.gz <www/html directory>/ubuntu/install/netboot/ubuntu-installer/amd64/initrd.gz 
```

#### Step 5

Manually verify DHCP server is running or not, using the given command below:

```
sudo systemctl status isc-dhcp-server.service
```

State should be active running.
If it is not running, then double check the hosts.yaml file and look
at /var/log/syslog for error messages.

Manually verify tftp-hpa service is running or not, using the given
command below:

```
sudo systemctl status tftpd-hpa
```

State should be active running.

Manually verify apache2 service is running or not, using the given
command below:

```
sudo systemctl status apache2
```

State should be active running.

#### Step 6
Go to root directory of the project (e.g. `snaps-boot`)

##### When PXE Server is either ubuntu or centos
Run `iaas_launch.py` as shown below:
```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -b
```
This will provision either ubuntu or centos OS on host machines, depending on the PXE Server.

##### When PXE Server is both ubuntu and centos
To provision ubuntu OS on host machines, Run `iaas_launch.py` as shown below:
```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -b ubuntu
```
or  

To provision ubuntu OS on host machines, Run `iaas_launch.py` as shown below:
```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -b centos
```

This will boot host machines (controller/compute nodes), select
NIC Controller (PXE client enabled) to use network booting.

Your OS provisioning will start and will get completed in about 20
minutes.  The time will vary depending on your network speed and
ip aserver boot times.

This will also set the static ip for the target hosts.

>:warning: This step will reboot each target server when it is done.  
Wait a few minutes then ping and/or ssh each target server to verify  
it is back up. 

#### Step 7 (optional)

The -s option can be maintained as a troubleshooting tool for static ip 
configuration 

Go to root directory of the project (e.g. `snaps-boot`)

Execute this step only if static IPs to be assigned to host machines.

Run `iaas_launch.py` as shown below:
```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -s
```
>:warning: This step will reboot each target server when it is done.  
Wait a few minutes then ping and/or ssh each target server to verify  
it is back up. 

> Note: This is an optional step and the same functionality is also present in
-b option (static ip of target host are set after pxe boot )

#### Step 8
Go to root directory of the project (e.g. `snaps-boot`)

Execute this step either for defining large memory pages or for
isolating CPUs between host and guest OS.

```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -i
```

> Note: This step is optional and should be executed only if CPU
isolation or large memory page provisioning is required.

## 5 Clean-up and Troubleshooting

### 5.1 Roll-back Isolated CPUs and Huge Pages

```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -ic
```

This will modify grub file on all host machines to remove isolated cpu
and huge page configuration and will boot the machine to default
configuration.

### 5.2 Roll-back Static IP Configuration and Change Default Routes
Back to Management Interface

```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -sc
```

This will remove the static config files present in  etc/network/interfaces.d/ folder.
this will remove static entries of the interfaces and will change back default route to 
management interface after reboot.

### 5.3 Roll-back of SNAPS-Boot Installation

```
sudo -i python $PWD/iaas_launch.py -f $PWD/conf/pxe_cluster/hosts.yaml -pc
```

This will stop DHCP, PXE and TFTP services on Build Server.
