#!/bin/bash

# Crash Bash on error
set -e

echo making sure we have pip3 and venv
if [ -x $pip3 ]
then
    echo pip3 already installed
else
    echo it was not installed, probably installing
    sudo apt install python3-pip -y >> logs/setup.log 2>> logs/error.log
fi

echo Installing Wheel on base python I guess
pip3 install wheel >> logs/setup.log 2>> logs/error.log
pip3 install virtualenv >> logs/setup.log 2>> logs/error.log
if [ -d venv ]
then
    echo venv was already present, hope it is the right one
else
    echo Installing venv
    sudo apt install python3-venv -y >> logs/setup.log 2>> logs/error.log
    python3 -m venv venv
fi
source venv/bin/activate
echo Installing Wheel on venv python I guess
pip install wheel >> logs/setup.log 2>> logs/error.log

echo installing and starting postgres from default Ubuntu repo
echo as per https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-22-04-quickstart

if [ -x $psql ]
then
    echo Installing Postgres
else
    echo it was not installed, probably installing
    sudo apt install python3-pip -y >> logs/setup.log 2>> logs/error.log
fi
sudo apt install -y postgresql postgresql-contrib libpq-dev >> logs/setup.log 2>> logs/error.log
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

echo Creating database fmtm
sudo -u postgres psql -c "CREATE DATABASE fmtm WITH OWNER fmtm;"

echo Done.
echo To use the utilities here, activate the virtual environment with:
echo source venv/bin/activate
echo
echo And type deactivate to get out when you are done.
