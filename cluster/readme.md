#**集群节点**
---

| 节点名 | 作用 |
|------|:---------:|
| Master节点 | 容器集群的管理节点 |
| 若干Node节点 | 容器集群的计算节点，容器运行在其上 |
| Registry | 镜像仓库节点，用于存放平台上所有应用的镜像 |
| NFS | 用作应用持久化存储的后端 |
| 监控节点 | 包括InfluxDB和Grafana，实现监控系统 |
| 管理平台 | 包括MySQL数据库（存储元数据）和web服务器 |

#**部署架构图**
---
![这里写图片描述](http://img.blog.csdn.net/20160518163122601)

#**部署流程**
---
我们现在按照如下步骤部署平台的各服务节点。

###**私有仓库**
私有仓库Registry用来保存用户以及管理员上传的镜像，K8S集群中的Node在拉取镜像时可以直接从Registry中以极快的速度拉取下来，实现更快速的部署应用。

	$ git clone https://github.com/wangtaoking1/hummer.git
	$ cd hummer/cluster
	$ sudo bash registry_install.sh

在安装Docker的过程中需要输入私有仓库的地址，直接按回车即可，默认为本机。

###**NFS Server**
NFS Server用来做数据持久化的，可以作为镜像存储后端以及存储
需要持久化的应用数据（日志，数据库数据等）。
在NFS　Server上运行如下命令安装NFS服务:

	$ git clone http://github.com/wangtaoking1/hummer.git
	$ cd hummer/cluster
	$ sudo bash nfs_install.sh

部署好NFS Server后，我们还需将该目录挂载到管理平台服务节点上，在管理平台服务节点上运行如下命令设置开机挂载：

	# apt-get install nfs-common
	# mkdir /hummer
	# showmount -e nfs_server_ip
	# mount -t nfs nfs_server_ip:/hummer /hummer
	# echo "nfs_server_ip:/hummer /hummer nfs defaults 0 0" >>/etc/fstab

###**K8S集群**
由于该部分部署工作比较复杂，所以没有花大量时间去写自动化部署脚本了，而是直接使用官方的部署脚本。现在只要按着如下步骤操作即可部署好K8S集群。

#####**准备工作**
设计好集群结构，为每一台机器安装好操作系统，需要Ubuntu 14.04 64bit，配置好IP地址及主机名等，安装git，用于下载安装脚本，开启SSH服务，用于支持远程登录安装K8S。
在Master节点上运行如下命令配置好能够从Master节点免密钥登录到其他节点上。

	$ ssh-keygen
	$ ssh-copy-id user@node1_ip
	$ ssh-copy-id user@node2_ip
	$ ssh-copy-id user@node3_ip

#####**Docker安装**
K8S是基于Docker的开源平台，所以我们首先需要在集群的每一个节点上安装好Docker。这里可以直接使用已写好的脚本进行自动化安装。
在每个Node上执行以下命令进行安装。

	$ git clone https://github.com/wangtaoking1/hummer.git
	$ cd hummer/cluster
	$ sudo bash docker_install.sh
在安装的过程中需要输入私有仓库的地址，用于快速下载镜像。

在安装的过程中需要用到镜像pause（如果部署附加的DNS服务还需要下载etcd，kube2sky，skydns，exechealthz等镜像，DNS服务可选），但是由于GFW的原因，通常会下载失败，所以我们需要提前从docker.io下载这些镜像。

	$ cd hummer/cluster
	$ sudo bash download_k8s_images.sh

需要使用NFS做持久化volume后端，因此需要在每一个集群节点上安装nfs-common，这样才能成功访问nfs server。

	# apt-get install nfs-common

#####**下载脚本**
首先从kubernetes官方仓库中下载安装脚本，然后下载二进制可执行文件。这里是下载的1.2.0版本的kubernetes，相关的组件版本为flannel=0.5.5，etcd=2.2.1，k8s=1.1.8。

	$ git clone https://github.com/kubernetes/kubernetes.git
	$ cd kubernetes/cluster/ubuntu
	$ ./download-release.sh

如果下载不成功，那么就用root下载，完成之后将文件所有者设置为原来的账户。

#####**修改配置**
修改kubernetes/cluster/ubuntu目录下的config-default.sh文件。

	export nodes=${nodes:-"wangtao@192.168.0.201 wangtao@192.168.0.202 wangtao@192.168.0.203"}

	export role=${role:-"a i i"}

	export NUM_MINIONS=${NUM_MINIONS:-2}

	export SERVICE_CLUSTER_IP_RANGE=${SERVICE_CLUSTER_IP_RANGE:-10.0.1.0/24}

	export FLANNEL_NET=${FLANNEL_NET:-172.16.0.0/16}

	DOCKER_OPTS=${DOCKER_OPTS:-"-H 0.0.0.0:2357 --registry-mirror=http://aad0405c.m.daocloud.io --insecure-registry=192.168.0.10:5000"}

这里最后一行的"192.168.0.10:5000"为镜像仓库的地址。

#####**部署**
直接在Master节点上运行脚本进行安装，在安装的过程中需要输入密码。

	$ cd kubernetes/cluster
	$ export KUBERNETES_PROVIDER=ubuntu
	$ ./kube-up.sh

如果需要添加新的Node到集群中，那么可以先使用kube-down.sh脚本将集群停掉，然后修改配置文件config-default.sh，重新运行kube-up.sh即可运行新的集群。

#####**测试**
将kubectl文件的路径加入到PATH中，或者将其拷入到/usr/local/bin中，这样便可直接使用kubectl工具对集群进行操作。

	$ kubectl get node
如果正确显示各节点信息，那么就部署成功了。

###**管理平台**
管理平台基于Python3开发，需要安装Python3的一些软件包，在项目主目录的requirements.txt文档列出。

首先安装虚拟环境python-virtualenv。

	$ sudo apt-get install python-virtualenv
	$ virtualenv -p /usr/bin/python3 py3env
	$ souce py3env/bin/active
安装git，下载项目源码包，创建文件夹以及修改settings.py文件。

	$ git clone https://github.com/wangtaoking1/hummer.git

	#安装依赖包
	$ sudo apt-get install python3-dev libmysqlclient-dev
	$ pip install -r requirements.txt

	#启动服务
	$ mkdir files logs
	$ vim hummer/settings.py      #修改最后几行参数为实际环境
	$ python manage.py createsuperuser   #创建管理员
	$ python manage.py runserver 0.0.0.0:80

###**监控系统**
监控部分为可选。
整套监控系统需要部署3个组件：heapster服务，InfluxDB数据库，Grafana服务。

#####**heapster**
heapster是以容器的形式运行于k8s集群中的，建议提前下载好镜像wangtaoking1/heapster:canary，上传到私有仓库中，这样更容易部署成功。在Master节点上运行如下命令：

	$ git clone https://github.com/wangtaoking1/hummer.git
	$ cd hummer/cluster/monitoring
	$ kubectl create -f namespace.yaml      #创建kube-system命名空间

	#修改heapster.yaml文件中的参数
	$ vim heapster.yaml
	$ kubectl --namespace=kube-system create -f heapster.yaml
	$ kubectl --namespace=kube-system create -f heapstersvc.yaml

#####**InfluxDB & Grafana**
首先需在节点上安装Docker，可以使用前面的脚本进行自动安装。下载镜像wangtaoking1/heapster_grafana:v2.5.0和wangtaoking1/heapster_influxdb:v0.6。然后在节点上运行如下命令部署监控系统：

	$ cd monitoring
	$ vim influxdb_grafana.sh        #修改配置
	$ sudo bash influxdb_grafana.sh

