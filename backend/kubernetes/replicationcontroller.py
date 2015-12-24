

class Controller(object):
    """
    Kubernetes replicationcontroller, each application corresponding to a rc.

    Parameters:
    name: application name.
    replicas: the number of pods.
    image_name: the image name for the container.
    ports: the ports of the container.
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

    def __init__(self, name, image_name, replicas=1, ports=None, commands=None,
        args=None, envs=None):
        self._body['metadata']['name'] = name
        self._body['spec']['template']['metadata']['labels']['app'] = name
        self._body['spec']['replicas'] = replicas
        self._container['name'] = name
        self._container['image'] = image_name
        self._container['command'] = commands
        self._container['args'] = args
        if ports:
            self.set_ports(ports)
        if envs:
            self.set_envs(envs)

    def set_ports(self, ports):
        """
        Open ports for the containers.

        Parameters:
        ports: the list of open ports.
        """
        for port in ports:
            self._container['ports'].append({'containerPort': port})

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
