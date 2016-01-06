#**部署架构图**
---
![物理架构图](http://img.blog.csdn.net/20151031165906356)

我们现在按照如下步骤部署私有仓库Registry和K8S集群。

#**私有仓库**
---
私有仓库Registry用来保存用户以及管理员上传的镜像，K8S集群中的Node在拉取镜像时可以直接从Registry中以极快的速度拉取下来，实现更快速的部署应用。

	$ git clone https://github.com/wangtaoking1/hummer.git
	$ cd hummer/cluster
	$ sudo bash registry_install.sh

在安装Docker的过程中需要输入私有仓库的地址，直接按回车即可，默认为本机。

#**NFS Server**
---
NFS Server用来做数据持久化的，可以作为镜像存储后端以及存储
需要持久化的应用数据（日志，数据库数据等）。
在NFS　Server上运行如下命令安装NFS服务:

	$ git clone http://github.com/wangtaoking1/hummer.git
	$ cd hummer/cluster
	$ sudo bash nfs_install.sh

部署好NFS Server后，我们还需将该目录挂载到平台API Server上，在API Server上运行如下命令设置开机挂载：

	# apt-get install nfs-common
	# mkdir /hummer
	# echo "nfs_server_ip:/hummer /hummer nfs 0 0" >>/etc/fstab

#**K8S集群**
---
由于该部分部署工作比较复杂，所以没有花大量时间去写自动化部署脚本了，只要按着如下步骤操作即可部署好K8S集群。

###**准备工作**
设计好集群结构，为每一台机器安装好操作系统，需要Ubuntu 14.04 64bit，配置好IP地址及主机名等，安装git，用于下载安装脚本，开启SSH服务，用于支持远程登录安装K8S。
在Master节点上运行如下命令配置好能够从Master节点免密钥登录到其他节点上。

	$ ssh-keygen
	$ ssh-copy-id user@node1_ip
	$ ssh-copy-id user@node2_ip
	$ ssh-copy-id user@node3_ip

###**Docker安装**
K8S是基于Docker的开源平台，所以我们首先需要在集群的每一个节点上安装好Docker。这里可以直接使用已写好的脚本进行自动化安装。
在每个Node上执行以下命令进行安装。

	$ git clone https://github.com/wangtaoking1/hummer.git
	$ cd hummer/cluster
	$ sudo bash docker_install.sh
在安装的过程中需要输入私有仓库的地址，用于快速下载镜像。

由于GFW，为了能够成功安装，须先下载安装过程中会用到的pause镜像。

	# docker pull docker.io/kubernetes/pause
	# docker tag kubernetes/pause gcr.io/google_containers/pause:0.8.0
	# docker tag gcr.io/google_containers/pause:0.8.0 gcr.io/google_containers/pause

需要使用NFS做持久化volume后端，因此需要在每一个集群节点上安装nfs-common，这样才能成功访问nfs server。

	# apt-get install nfs-common


###**下载脚本**
首先从kubernetes官方仓库中下载安装脚本，然后下载二进制可执行文件。

	$ git clone https://github.com/kubernetes/kubernetes.git
	$ cd kubernetes/cluster/ubuntu
	$ export FLANNEL_VERSION="0.5.0"
	$ export ETCD_VERSION="2.2.0"
	$ export KUBE_VERSION="1.0.6"
	$ ./build.sh
	# 新版的k8s这里运行的是download-release.sh

如果下载不成功，那么就用root下载，完成之后将文件所有者设置为原来的账户。

###**修改配置**
修改kubernetes/cluster/ubuntu目录下的config-default.sh文件。

	export nodes=${nodes:-"wangtao@192.168.0.201 wangtao@192.168.0.202 wangtao@192.168.0.203"}

	export role=${role:-"a i i"}

	export NUM_MINIONS=${NUM_MINIONS:-2}

	export SERVICE_CLUSTER_IP_RANGE=${SERVICE_CLUSTER_IP_RANGE:-10.0.1.0/24}

	export FLANNEL_NET=${FLANNEL_NET:-172.16.0.0/16}

	DOCKER_OPTS=${DOCKER_OPTS:-"-H 0.0.0.0:2357 --registry-mirror=http://aad0405c.m.daocloud.io --insecure-registry=192.168.0.10:5000"}

###**部署**
直接在Master节点上运行脚本进行安装，在安装的过程中需要输入密码。

	$ cd kubernetes/cluster
	$ export KUBERNETES_PROVIDER=ubuntu
	$ ./kube-up.sh

如果需要添加新的Node到集群中，那么可以先使用kube-down.sh脚本将集群停掉，然后修改配置文件config-default.sh，重新运行kube-up.sh即可运行新的集群。

###**测试**
将kubectl文件的路径加入到PATH中，或者将其拷入到/usr/local/bin中，这样便可直接使用kubectl工具对集群进行操作。

	$ kubectl get node
如果正确显示各节点信息，那么就部署成功了。



