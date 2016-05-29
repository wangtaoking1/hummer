

class Controller(object):
    """
    Kubernetes replicationcontroller, each application corresponding to a rc.

    Parameters:
    name: application name.
    replicas: the number of pods.
    image_name: the image name for the container.
    tcp_ports: a dict, the tcp ports of the containers. For example: {
        "http": 80, "https": 443}
    udp_ports: a dict, the udp ports of the containers.
    commands: the commands which the container runs when start.
    envs: a dict for example: {"MYSQL_HOST": "localhost", "PORT": "3306"}
    volumes: a dict, for example: {"volume_name": "mount_path"}
    """
    _resource_limit = {
        "requests": {
            "memory": None,
            "cpu": None
        },
        "limits": {
            "memory": None,
            "cpu": None
        }
    }

    _container = {
        "name": None,
        "image": None,
        "resources": _resource_limit,
    }

    _body = {
        "apiVersion": "v1",
        "kind": "ReplicationController",
        "metadata": {
            "name": None
        },
        "spec": {
            "replicas": None,
            "template": {
                "metadata": {
                    "labels": {
                        "app": None
                    }
                },
                "spec": {
                    "containers": [_container],
                }
            }
        }
    }

    def __init__(self, name, image_name, cpu, memory, replicas=1,
        tcp_ports=None, udp_ports=None, commands=[], args=[], envs={},
        volumes={}):
        self._resource_limit['requests']['memory'] = memory
        self._resource_limit['requests']['cpu'] = cpu
        self._resource_limit['limits']['memory'] = memory
        self._resource_limit['limits']['cpu'] = cpu
        self._body['metadata']['name'] = name
        self._body['spec']['template']['metadata']['labels']['app'] = name
        self._body['spec']['replicas'] = replicas
        self._container['name'] = name
        self._container['image'] = image_name
        if commands:
            self._container['command'] = commands
        if args:
            self._container['args'] = args

        self._container['ports'] = []
        if tcp_ports:
            self.set_ports("TCP", tcp_ports)
        if udp_ports:
            self.set_ports("UDP", udp_ports)

        self._container['env'] = []
        if envs:
            self.set_envs(envs)

        self._container['volumeMounts'] = []
        if volumes:
            self._body['spec']['template']['spec']['volumes'] = []
            self.set_volumes(volumes)

    def set_ports(self, protocol, ports):
        """
        Open ports for the containers.

        Parameters:
        ports: the dict of open ports.
        """
        assert(protocol in ['TCP', 'UDP'])

        for name, port in ports.items():
            self._container['ports'].append({
                'name': name,
                'protocol': protocol,
                'containerPort': port})

    def set_envs(self, envs):
        """
        Set the environments.

        Parameters:
        envs: a dict for example: {"MYSQL_HOST": "localhost", "PORT": "3306"}
        """
        for key, value in envs.items():
            env = {'name': key, 'value': value}
            self._container['env'].append(env)

    def set_volumes(self, volumes):
        """
        Set the volumes.

        Parameters:
        volumes: a dict, for example: {"volume_name": "mount_path"}
        """
        assert(isinstance(volumes, dict))
        for name, path in volumes.items():
            self._container['volumeMounts'].append({
                "mountPath": path,
                "name": name
            })

            self._body['spec']['template']['spec']['volumes'].append({
                "name": name,
                "persistentVolumeClaim": {
                    "claimName": name
                }
            })

    @property
    def body(self):
        return self._body
