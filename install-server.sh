#!/bin/bash
#
# Install Coalition server
# (c) Geomage 2015
#

echo "Install python3 support"
yum install -y python3-twisted
echo "Install coalition-server"
chmod +x coalition-server
cp coalition-server /etc/init.d/
service coalition-server start
chkconfig coalition-server on

echo "coalition-server installed to your system and configured for auto startup"
echo "for start coalition-server please use command #service coalition-server start"
