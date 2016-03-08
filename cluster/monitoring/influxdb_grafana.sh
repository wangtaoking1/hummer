#!/bin/bash
# Description: install influxdb and grafana
# Version: 0.1
#
# Author: wangtao 479021795@qq.com
# Date: 2016/01/08

set -o xtrace

function download_images() {
    docker pull kubernetes/heapster_influxdb:v0.6
    docker pull kubernetes/heapster_grafana:v2.5.0
}

if [[ $UID -ne 0 ]]; then
    echo "Not root user. Please run as root."
    exit 0
fi

download_images

mkdir -p /hummer-monitoring /hummer-monitoring/data /hummer-monitoring/var

# start influxdb instance
docker run -d --restart=always -p 8083:8083 -p 8086:8086 -v /hummer-monitoring/data:/data --name heapster_influxdb kubernetes/heapster_influxdb:v0.6

INFLUXDB_SERVICE_IP="192.168.0.15"
# start grafana instance
docker run -d --restart=always -p 3000:3000 -v /hummer-monitoring/var:/var -e "INFLUXDB_SERVICE_URL=http://${INFLUXDB_SERVICE_IP}:8086" --name heapster_grafana kubernetes/heapster_grafana:v2.5.0
