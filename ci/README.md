
# Continuous Integration ReadMe

## 1 Introduction

This document serves as a guide for developers to test this project
in a Continuous Integration (CI) environment.  It can also be used
to evaluate this project for new users.

To test the installation process, the scripts under the ci directory
can create compute, networking and storage resources to run SNAPS-boot
inside an open stack environment.  

iPXE image is used to PXE boot from VM.

IPMI is not available in this environment and is not tested.

This will enable more testing and development to occur than would be
supported on available physical hardware.

### 1.1 Terms and Conventions

The terms and typographical conventions used in this document are listed and
explained in below table.

| Convention | Usage |
| ---------- | ----- |
| CI Server | This is the physical or virtual server were we run the CI script. The CI server will connect to an OpenStack instance to create the environment|
| Build Server | The VM which will install snaps-boot |
| Kickseed VM | The VMs that are installed by snaps-boot |
### 1.2 Acronyms

The acronyms expanded below are fundamental to the information in this
document.

| Acronym | Explanation |
| ------- | ----------- |
| CI | Continuous Integratoin |
| VM | Virtual Machine |

## 2 CI server setup

1. Download and install snaps-oo.
```
git clone https://gerrit.opnfv.org/gerrit/snaps
sudo apt install python git python2.7-dev libssl-dev python-pip
sudo pip install -e snaps/snaps
```

2. Download and set branch of snaps-openstack to test
```
git clone https://github.com/cablelabs/snaps-boot.git
cd snaps-boot
git checkout <branch>
```
3.  Configure the environment file.
This file will provide information about the configuration and the
OpenStack isntance which snaps-openstack will be installed on.
lab3.yaml
```
---
build_num: ci-launcher

# These values are variable
admin_user: admin
admin_proj: admin
admin_pass: something
auth_url: http://10.197.113.30:5000
id_api_version: 3
proxy_host:
proxy_port:
ssh_proxy_cmd:

ext_net: external
ext_subnet: external-net

src_snaps_boot_dir: /home/ubuntu/snaps-boot
src_copy_dir: /tmp
local_snaps_boot_dir: /home/ubuntu/snaps-boot

os_pxe_user_pass: password

ctrl_ip_prfx: 10.0.0
admin_ip_prfx: 10.1.0
priv_ip_prfx: 10.1.1
pub_ip_prfx: 10.1.2

build_kp_pub_path: /tmp/pxe-kp-lab1-launcher.pub
build_kp_priv_path: /tmp/pxe-kp-lab1-launcher

pxe_machine_user: root
pxe_machine_pass: Pa$$w0rd

hosts_yaml_target_path: /tmp/hosts.yaml
```
4. Launch the test
This is best to do in a screen session and redirect the output.
It will take about an hour to run.
```
cd snaps/examples
python ./launch.py -t /home/ubuntu/snaps-boot/ci/snaps/snaps_pxe_tmplt.yaml \
-e lab3.yaml -d
```
5. Clean the environment
This will remove the account, VMs, netwoks and storage that was created
in the install.
```
python ./launch.py -t /home/ubuntu/snaps-boot/ci/snaps/snaps_pxe_tmplt.yaml \
-e lab3.yaml -c
```
