#!/usr/bin/env bash
# Copyright 2017 ARICENT HOLDINGS LUXEMBOURG SARL and Cable Television Laboratories, Inc.
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

checkStatus () {
if [ $command_status != "0" ]
then
echo " last command $2 not executed successfully :: exit the script"
exit 0
else
echo " last command $2 executed successfully "
fi
}


echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "apt-get install apt-cacher-ng"
echo "++++++++++++++++++++++++++++++++++++++++++++++"
apt-get install -y apt-cacher-ng
command_status=$?
checkStatus $command_status "install apt-cache-eng  using apt-get"
sleep 5


echo "++++++++++++++++++++++++++++++++++++++++++++++"
echo "apt-get install ipmitool"
echo "++++++++++++++++++++++++++++++++++++++++++++++"
apt-get install -y ipmitool
command_status=$?
checkStatus $command_status "install  ipmitool using apt-get"
sleep 5
