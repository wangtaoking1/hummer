

class Service(object):
    """
    Kubernetes service, each application has a service.

    Parameters:
    name: application name.
    tcp_ports: a dict, the tcp ports of the service. For example: {
        "http": 80, "https": 443}.
    udp_ports: a dict, the udp ports of the service.
    is_public: boolean.
    """
    _body = {
        "apiVersion": "v1",
        "kind": "Service",
        "metadata": {
            "name": None,
            "labels": {
                "app": None
            }
        },
        "spec": {
            "selector": {
                "app": None
            },
            "ports": [],
            "type": "ClusterIP",
            "sessionAffinity": "None"
        }
    }

    def __init__(self, name, tcp_ports=None, udp_ports=None, is_public=False,
        session_affinity=False):
        self._body['metadata']['name'] = name
        self._body['metadata']['labels']['app'] = name
        self._body['spec']['selector']['app'] = name

        self._body['spec']['ports'] = []
        if tcp_ports:
            self.set_ports("TCP", tcp_ports)
        if udp_ports:
            self.set_ports("UDP", udp_ports)

        if is_public:
            self._body['spec']['type'] = "NodePort"
        else:
            self._body['spec']['type'] = "ClusterIP"
        if session_affinity:
            self._body['spec']['sessionAffinity'] = "ClientIP"
        else:
            self._body['spec']['sessionAffinity'] = "None"

    def set_ports(self, protocol, ports):
        """
        Open port for the service.
        """
        assert(protocol in ['TCP', 'UDP'])
        for name, port in ports.items():
            self._body['spec']['ports'].append({
                'name': name,
                'protocol': protocol,
                'port': port})

    @property
    def body(self):
        return self._body
