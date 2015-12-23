import json
import requests
import logging

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
        print(res)
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
        body = {'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': {}
                }
        body['metadata']['name'] = name

        self._send_request('POST', 'namespaces', body=body)

    def delete_namespace(self, name):
        """
        Delete namespace called name.
        """
        res = self._send_request('DELETE', 'namespaces/{}'.format(name))
        print(res)



