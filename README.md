# SNAPS-Boot

SNAPS-Boot is the fundamental building block for the SDN/NFV Application
Platform and Stack (SNAPS<sup>TM</sup>) we are developing at
[CableLabs](http://cablelabs.com/). It performs a Linux install and network
setup for a bare metal machine.

If you're working with Software Defined Networks (SDN), Network
Function Virtualization (NFV) or just building your own cloud, then this is
where you want to start.

| TIP: [SNAPS-OpenStack](https://github.com/cablelabs/snaps-openstack) is where you
should go next.

## Getting started

To get started, you'll want to read the [SNAPS-Boot install
guide](doc/source/install/install.md). The fun really begins with the
[installation
steps](https://github.com/cablelabs/snaps-boot/blob/master/doc/source/install/install.md#4-installation-steps).
That's where you'll be able to clone this repo and commence building:

```
$ git clone https://github.com/cablelabs/snaps-boot.git
```

If you're new to git and GitHub, be sure to check out the [Pro
Git](https://git-scm.com/book/en/v2) book. [GitHub
Help](https://help.github.com/) is also outstanding.

## Known issues

There is an issue with the Ubuntu installer attempting to use only the first
interface as enumerated alphabetically by the network device renaming code in
the kernel. This can be a problem when re-imaging the pod nodes.

The workaround is to connect a monitor to each node and set up the network
interface by hand or to reconfigure the PXE section of the `hosts.yaml` file to
indicate the interface that the Ubuntu installer is trying to use.

## Contributing

SNAPS-Boot was originally built by [CableLabs](http://cablelabs.com/) and
[Aricent](https://www.aricent.com/), but we could use your help! Check out our
[contributing guidelines](CONTRIBUTING.md) to get started.

## Other important stuff

We use an [Apache 2.0 License](LICENSE) for SNAPS-Boot.

Questions? Just send us an email at
[snaps@cablelabs.com](mailto:snaps@cablelabs.com) or join the conversation:
[![IRC](https://www.irccloud.com/invite-svg?channel=%23cablelabs-snaps&amp;hostname=irc.freenode.net&amp;port=6697&amp;ssl=1)](https://www.irccloud.com/invite?channel=%23cablelabs-snaps&amp;hostname=irc.freenode.net&amp;port=6697&amp;ssl=1).
