#!/bin/bash

echo making sure we have pip3 and venv
if [ -x $pip3 ]
then
    echo setting up pip3
else
    echo it was not installed, probably installing
    sudo apt install python3-pip -y >> provisioning/setup.log 2>> provisioning/error.log
fi

sudo apt install python3-venv -y >> provisioning/setup.log 2>> provisioning/error.log

if [ -d venv ]
then
    echo venv was already present, hope it is the right one
else
    python3 -m venv venv
fi

echo creating and activating virtual environment
pip3 install wheel >> provisioning/setup.log 2>> provisioning/error.log
pip3 install virtualenv >> provisioning/setup.log 2>> provisioning/error.log
source venv/bin/activate
pip install wheel >> provisioning/setup.log 2>> provisioning/error.log

echo installing and starting postgres from default Ubuntu repo
echo as per https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-22-04-quickstart
sudo apt install -y postgresql postgresql-contrib libpq-dev >> provisioning/setup.log 2>> provisioning/error.log
sudo systemctl start postgresql.service

echo Creating postgres user fmtmk
# TODO This is a pretty obvious password (it's md5 hashed).
# Generate another one using bash:
# echo -n passwordusername | md5sum
# and paste the result into the following command
# with the prefix 'md5' (the hash below begins with 540e)
sudo -u postgres psql -c "CREATE ROLE fmtm WITH PASSWORD 'md5540e7aa2739a14c6f2e6f07fd09c67f1';"
sudo -u postgres psql -c "ALTER ROLE fmtm WITH LOGIN"
sudo -u postgres psql -c "ALTER ROLE fmtm WITH SUPERUSER"

echo Creating database odm360
sudo -u postgres psql -c "CREATE DATABASE fmtm WITH OWNER fmtm;"

echo Done.
echo To use the utilities here, activate the virtual environment with:
echo source venv/bin/activate
echo
echo And type deactivate to get out when you are done.
