"""
Created on April 21, 2018

@author: Isaiah Sierra-Baron
"""
import sys, os, commands

failed_cmds = []

def system(cmd):
    failure, output = commands.getstatusoutput(cmd)
    if failure:
        print 'Command %s failed to install\n' % cmd
        failed_cmds.append(cmd)
        #sys.exit(1)
        print output
    else:
        print 'Command %s successfully executed' %cmd

#       apt-get install python
system('apt-get install -y  python python-pip python-dev python-pathlib')

#   apt-get install apt-cacher-ng
system('apt-get install -y apt-cacher-ng')

#   apt-get install python-yaml
system('apt-get install python-yaml')

#   apt-get install ansible
system('apt-get install -y ansible')

#   apt-get install dos2unix
system('apt-get install -y dos2unix')

#   apt-get install ipmitool
system('apt-get install -y ipmitool')

#   apt-get install sshpass
system('apt-get install -y sshpass')

#   ssh-keygen  generation

#   apt-get install openjdk
system('sudo apt-get install -y openjdk-8-jdk')

#   pip install cryptography
system('sudo pip install cryptography')

if len(failed_cmds) > 1:
    print 'Failed to execute the following commands: '
    for line in failed_cmds:
        print line
