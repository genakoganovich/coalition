RHEL 8:
sudo pip3 install twisted
wget https://objectstorage.eu-frankfurt-1.oraclecloud.com/p/Fv7LpHPSWOrQnY9kw5X4J_XrVvxCyTtyvsbGLna2lHr1wsyBxzEciP-AT6Cfwv95/n/frnve8smtr6u/b/external_users/o/coalition-server-v3.0.tar.gz
tar -xvnf coalition-server-v3.0.tar.gz
cd coalition-server-v3.0/

mkdir /opt/coalition-server
sudo mkdir /opt/coalition-server
sudo chown rocky:rocky /opt/coalition-server
cp -r * /opt/coalition-server/

chmod +x coalition-server
sudo cp coalition-server /etc/init.d/
sudo service coalition-server start
sudo chkconfig coalition-server on


