#! /usr/bin/env bash


# Reliably detect the actual folder that the install script is in.
# Taken from this stackoverflow answer:
#    https://stackoverflow.com/a/246128/5729206
SOURCE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"



if [[ $EUID -ne 0 ]]
then
    echo "Install must be run as root."
    exit -1
fi

if systemctl is-active vhf-tracker
then
    systemctl stop vhf-tracker
fi

# install files
mkdir -p /opt/vhf-tracker
rm -r /opt/vhf-tracker/*
install "$SOURCE_DIR" /opt/vhf-tracker/

# install and enable systemd unit file
ln -s -T /opt/vhf-tracker/vhf-tracker.service /etc/systemd/system/vhf-tracker.service
systemctl daemon-reload
systemctl enable vhf-tracker

echo "Installed vhf-tracker to /opt/vhf-tracker."
echo "It will be run on startup."
echo "Type 'systemctl start vhf-tracker' to start it now."
