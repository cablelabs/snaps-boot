# snaps-boot
Linux install and network setup for SNAPS

Email [questions](mailto:snaps@cablelabs.com) or open an [issue](https://github.com/cablelabs/snaps-boot/issues)

Join the conversation:
[![IRC](https://www.irccloud.com/invite-svg?channel=%23cablelabs-snaps&amp;hostname=irc.freenode.net&amp;port=6697&amp;ssl=1)](https://www.irccloud.com/invite?channel=%23cablelabs-snaps&amp;hostname=irc.freenode.net&amp;port=6697&amp;ssl=1)

There is an issue with the Ubuntu installer attempting to use only the first
interface as enumerated alphabetically by the network device renaming code 
in the kernel.  This can be a problem when re-imaging the pod nodes.  

The work around is to connect a monitor to each node and set up the network 
interface by hand or to reconfigure the PXE section of the hosts.yaml file 
to indicate the interface that the Ubuntu installer is trying to use.
