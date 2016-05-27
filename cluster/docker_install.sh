#!/bin/bash
# Description: install docker daemon and client
# Version: 0.1
#
# Author: wangtao 479021795@qq.com
# Date: 2015/10/28

set -o xtrace

function update_kernel() {
    apt-get update
    apt-get install linux-image-generic-lts-raring linux-headers-generic-lts-raring

    reboot
}

function add_docker_source() {
    echo "deb https://get.docker.com/ubuntu docker main" > /etc/apt/sources.list.d/docker.list
}

# install apt-transport-https support and Docker registry key
function install_key() {
    apt-get install apt-transport-https -y
    apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 36A1D7869245C8950F966E92D8576A8BA88D21E9
    apt-key adv --keyserver keyserver.ubuntu.com --recv-keys D8576A8BA88D21E9

    return 0
}

# update time for every 30 minutes
function set_ntp() {
    crontab -l > /tmp/crontab.bak
    echo '30/* * * * * root /usr/sbin/ntpdate ntp.api.bz' >> /tmp/crontab.bak
    crontab /tmp/crontab.bak
}

# install bridge-utils
function install_brctl() {
    apt-get install bridge-utils
}


if [[ $UID -ne 0 ]]; then
    echo "Not root user. Please run as root."
    exit 0
fi

system_version=$(cat /etc/issue | cut -d " " -f2)
if [[ $system_version < "14.04" ]]; then
    echo "Use Ubuntu 14.04 or newer."
    exit 0
fi

bash ./update_source.sh
add_docker_source
install_key

apt-get update -y
apt-get install -y lxc-docker

docker -v

# configure ntp
set_ntp

# install brctl
install_brctl

# Set Docker private registry address
read -p "Input private registry address(192.168.0.1:5000): " registry_address
if [[ -z $registry_address ]]; then
    registry_address="127.0.0.1:5000"
fi
# Add Docker registry mirror to speed up image download
sed -i "s|.*DOCKER_OPTS=.*|DOCKER_OPTS=\"-H 0.0.0.0:2357 -H unix:///var/run/docker.sock --registry-mirror=http://aad0405c.m.daocloud.io --insecure-registry=${registry_address}\"|g" /etc/default/docker

service docker restart

