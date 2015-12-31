

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
    """
    _container = {
        "name": None,
        "image": None,
        "ports": [],
        "command": [],
        "args": [],
        "env": []
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
                    "containers": [_container]
                }
            }
        }
    }

    def __init__(self, name, image_name, replicas=1, tcp_ports=None,
        udp_ports=None, commands=[], args=[], envs=[]):
        self._body['metadata']['name'] = name
        self._body['spec']['template']['metadata']['labels']['app'] = name
        self._body['spec']['replicas'] = replicas
        self._container['name'] = name
        self._container['image'] = image_name
        self._container['command'] = commands
        self._container['args'] = args
        self._container['ports'] = []
        if tcp_ports:
            self.set_ports("TCP", tcp_ports)
        if udp_ports:
            self.set_ports("UDP", udp_ports)
        self._container['env'] = []
        if envs:
            self.set_envs(envs)

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

    @property
    def body(self):
        return self._body
