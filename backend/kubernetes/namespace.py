

class Namespace(object):
    """
    Kubernetes namespace, each user corresponding to a namespace.
    """
    _body = {
        'apiVersion': 'v1',
        'kind': 'Namespace',
        'metadata': {}
    }

    def __init__(self, name):
        self._body['metadata']['name'] = name

    @property
    def body(self):
        return self._body

