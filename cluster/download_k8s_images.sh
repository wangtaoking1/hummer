#!/bin/bash
# Description: download k8s install images
# Version: 0.1
#
# Author: wangtao 479021795@qq.com
# Date: 2016/01/08

set -o xtrace

# for k8s install
function download_pause() {
    docker pull docker.io/kubernetes/pause
    docker tag kubernetes/pause gcr.io/google_containers/pause:0.8.0
    docker rmi kubernetes/pause
}

# for kube-dns
function download_etcd() {
    docker pull docker.io/kubernetes/etcd
    docker tag kubernetes/etcd gcr.io/google_containers/etcd:2.0.9
    docker rmi kubernetes/etcd
}

# For kube-dns
function download_kube2sky() {
    docker pull docker.io/kubernetes/kube2sky
    docker tag kubernetes/kube2sky gcr.io/google_containers/kube2sky:1.11
    docker rmi kubernetes/kube2sky
}

# For kube-dns
function download_skydns() {
    docker pull docker.io/kubernetes/skydns
    docker tag kubernetes/skydns gcr.io/google_containers/skydns:2015-10-13-8c72f8c
    docker rmi kubernetes/skydns
}

# For kube-dns
function download_exechealthz() {
    docker pull tupachydralisk/exechealthz:1.0
    docker tag tupachydralisk/exechealthz:1.0 gcr.io/google_containers/exechealthz:1.0
    docker rmi tupachydralisk/exechealthz:1.0
}

if [[ $UID -ne 0 ]]; then
    echo "Not root user. Please run as root."
    exit 0
fi

download_pause

# For kube-dns
# download_etcd
# download_kube2sky
# download_skydns
# download_exechealthz
