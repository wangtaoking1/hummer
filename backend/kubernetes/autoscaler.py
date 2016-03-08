class AutoScaler(object):
    """
    Kubernetes horizontal pod autoscaler, to autoscale the application.
    """
    _body = {
        "apiVersion": "extensions/v1beta1",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {
            "name": None
        },
        "spec": {
            "scaleRef": {
                "kind": "ReplicationController",
                "name:": None
            },
            "minReplicas": None,
            "maxReplicas": None,
            "cpuUtilization": {
                "targetPercentage": None
            }
        }
    }


    def __init__(self, name, minReplicas, maxReplicas, cpu_target):
        self._body['metadata']['name'] = name
        self._body['spec']['scaleRef']['name'] = name
        self._body['spec']['minReplicas'] = minReplicas
        self._body['spec']['maxReplicas'] = maxReplicas
        self._body['spec']['cpuUtilization']['targetPercentage'] = cpu_target

    @property
    def body(self):
        return self._body
