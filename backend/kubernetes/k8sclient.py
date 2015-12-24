import json
import requests
import logging

from backend.kubernetes.namespace import Namespace
from backend.kubernetes.replicationcontroller import Controller
from backend.kubernetes.service import Service

logger = logging.getLogger('hummer')


class KubeClient(object):
    """
    Kubernetes simple python client.
    API: http://kubernetes.io/third_party/swagger-ui/
    """
    _base_url = None
    def __init__(self, base_url):
        self._base_url = self.add_slash(base_url)

    @classmethod
    def add_slash(self, url):
        """
        Promote that the base url ends with '/'.
        """
        if url.endswith('/'):
            return url
        return url + '/'

    @property
    def base_url(self):
        return self._base_url

    def _send_request(self, method, path, query=None, body=None):
        """
        Send requests to k8s server and get the response.
        Returns a response dict.
        """
        url = self._base_url + path
        kwargs = {}
        if body:
            kwargs['data'] = json.dumps(body)

        try:
            res = getattr(requests, method.lower())(url, **kwargs)
        except Exception as error:
            logger.error(error)
            logger.error(res)
            return None

        return res.json()

    def list_nodes(self):
        """
        List all nodes.
        """
        res = self._send_request('GET', 'nodes')
        nodes = []
        for item in res.get('items'):
            nodes.append(item['metadata']['name'])
        return nodes

    def list_namespces(self):
        """
        List all namespaces.
        """
        res = self._send_request('GET', 'namespaces')
        namespaces = []
        for item in res.get('items'):
            namespaces.append(item['metadata']['name'])
        return namespaces

    def create_namespace(self, name):
        """
        Create namespace called name.
        """
        namespace = Namespace(name)

        self._send_request('POST', 'namespaces', body=namespace.body)

    def delete_namespace(self, name):
        """
        Delete namespace called name.
        """
        res = self._send_request('DELETE', 'namespaces/{}'.format(name))
        # print(res)

    def list_controllers(self, namespace):
        """
        List all replicationcontroller in the namespace.
        """
        path = 'namespaces/{}/replicationcontrollers'.format(namespace)
        res = self._send_request('GET', path)
        controllers = []
        for item in res.get('items'):
            controllers.append(item['metadata']['name'])
        return controllers

    def create_controller(self, namespace, name, image_name, replicas=1,
        tcp_ports=None, udp_ports=None, commands=None, args=None, envs=None):
        """
        Create a replicationcontroller.
        """
        controller = Controller(name, image_name, replicas, tcp_ports,
            udp_ports, commands, args, envs)
        path='namespaces/{}/replicationcontrollers'.format(namespace)

        self._send_request('POST', path, body=controller.body)

    def delete_controller(self, namespace, name):
        """
        Delete a replicationcontroller.
        """
        path='namespaces/{}/replicationcontrollers/{}'.format(namespace, name)
        self._send_request('DELETE', path)

    def list_services(self, namespace):
        """
        List all services in the namespace.
        """
        path = 'namespaces/{}/services'.format(namespace)
        res = self._send_request('GET', path)
        services = []
        for item in res.get('items'):
            services.append(item['metadata']['name'])
        return services

    def create_service(self, namespace, name, tcp_ports=None, udp_ports=None,
        is_public=False, session_affinity=False):
        """
        Create a service in namespace.
        """
        service = Service(name, tcp_ports, udp_ports, is_public,
            session_affinity)
        path='namespaces/{}/services'.format(namespace)

        res = self._send_request('POST', path, body=service.body)
        print(res)

    def delete_service(self, namespace, name):
        """
        Delete a service.
        """
        path='namespaces/{}/services/{}'.format(namespace, name)
        self._send_request('DELETE', path)

