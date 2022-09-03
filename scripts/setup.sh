#!/bin/bash

echo making sure we have pip3 and venv
if [ -x $pip3 ]
then
    echo setting up pip3
else
    echo it was not installed, probably installing
    sudo apt install python3-pip -y
fi

sudo apt install python3-venv -y

if [ -d venv ]
then
    echo venv was already present, hope it is the right one
else
    python3 -m venv venv
fi

echo creating and activating virtual environment
pip3 install wheel
pip3 install virtualenv
source venv/bin/activate
pip install wheel

echo installing and starting postgres from default Ubuntu repo
echo as per https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-22-04-quickstart
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql.service


echo Done.
echo To use the utilities here, activate the virtual environment with:
echo source venv/bin/activate
echo
echo And type deactivate to get out when you are done.
