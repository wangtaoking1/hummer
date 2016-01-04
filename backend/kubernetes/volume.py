
class PersistentVolume(object):
    """
    Kubernetes persistentvolume, each volume has a persistentvolume and
    persistentvolumeclaim.
    """
    _body = {
        "apiVersion": "v1",
        "kind": "PersistentVolume",
        "metadata": {
            "name": None
        },
        "spec": {
            "capacity": {
                "storage": None
            },
            "accessModes": ["ReadWriteMany"],
            "persistentVolumeReclaimPolicy": "Recycle",
            "nfs": {
                "path": None,
                "server": None
            }
        }
    }


    def __init__(self, name, capacity, nfs_path, nfs_server):
        self._body['metadata']['name'] = name
        self._body['spec']['capacity']['storage'] = capacity
        self._body['spec']['nfs']['path'] = nfs_path
        self._body['spec']['nfs']['server'] = nfs_server

    @property
    def body(self):
        return self._body


class PersistentVolumeClaim(object):
    """
    Kubernetes persistentvolumeclaim, each volume has a persistentvolume and
    persistentvolumeclaim.
    """
    _body = {
        "apiVersion": "v1",
        "kind": "PersistentVolumeClaim",
        "metadata": {
            "name": None
        },
        "spec": {
            "accessModes": ["ReadWriteMany"],
            "resources": {
                "requests": {
                    "storage": None
                }
            }
        }
    }

    def __init__(self, name, capacity):
        self._body['metadata']['name'] = name
        self._body['spec']['resources']['requests']['storage'] = capacity

    @property
    def body(self):
        return self._body
