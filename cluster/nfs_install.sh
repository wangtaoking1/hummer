#!/bin/bash
# Description: create a nfs server for persistent volume
# Version: 0.1
#
# Author: wangtao 479021795@qq.com
# Date: 2016/01/03

set -o xtrace

# update time for every 30 minutes
function set_ntp() {
    crontab -l > /tmp/crontab.bak
    echo '30/* * * * * root /usr/sbin/ntpdate ntp.api.bz' >> /tmp/crontab.bak
    crontab /tmp/crontab.bak
}


if [[ $UID -ne 0 ]]; then
    echo "Not root user. Please run as root."
    exit 0
fi

bash ./update_source.sh

# set ntp
set_ntp

# Install ntp
ntpdate -v
if [[ $? -ne 0 ]]; then
    echo "Install ntp..."
    bash ./ntp_install.sh
fi

apt-get install -y nfs-kernel-server nfs-common

mkdir /hummer
chmod -R 777 /hummer
cat >>/etc/exports <<EOF
/hummer *(rw,sync,no_root_squash,no_subtree_check)
EOF

# Restart service
service rpcbind restart
service nfs-kernel-server restart
