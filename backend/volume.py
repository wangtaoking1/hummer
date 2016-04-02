import logging, json
from threading import Thread

from django.conf import settings

from backend.models import Volume
from backend.kubernetes.k8sclient import KubeClient
from backend.utils import get_volume_nfs_dir
from backend.nfs import NFSRemoteClient, NFSLocalClient

logger = logging.getLogger('hummer')


class VolumeBuilder(object):
    """
    VolumeBuilder is a builder to create an volume for persistent data storagy.

    """
    volume = None

    def __init__(self, volume):
        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))

        self.volume = volume
        self.namespace = self.volume.project.user.username
        self.project_name = self.volume.project.name
        self.volume_name = self.project_name + '-' + self.volume.name
        self.capacity = str(self.volume.capacity) + self.volume.capacity_unit
        self.nfs_path = get_volume_nfs_dir(settings.NFS_BASE_DIR,
            self.namespace, self.project_name, self.volume.name)
        self.nfs_server = settings.NFS_IP

    def create_volume(self):
        """
        Create volume by multiple threading.
        """
        creating_thread = Thread(target=self._create_volume)
        creating_thread.start()

    def _create_volume(self):
        """
        First create a persistentvolume, then create a persistentvolumeclaim.
        """
        logger.info('User {} create a volume {} in project {}.'.format(
            self.namespace, self.volume.name, self.project_name))

        # create volume dir on nfs server
        if self._create_volume_dir_on_nfs():
            logger.info("Create dir {} on nfs server {} successfully.".format(
                self.nfs_path, self.nfs_server))
        else:
            logger.info("Create dir {} on nfs server {} failed.".format(
                self.nfs_path, self.nfs_server))
            self._update_volume_status(status='error')
            return None

        # create persistentvolume
        if self._create_persistentvolume():
            logger.info("Create persistentvolume {}-{} successfully.".format(
                self.namespace, self.volume_name))
        else:
            logger.info("Create persistentvolume {}-{} failed.".format(
                self.namespace, self.volume_name))
            self._update_volume_status(status='error')
            return None

        # create persistentvolumeclaim
        if self._create_persistentvolumeclaim():
            logger.info("Create persistentvolumeclaim {} successfully.".format(
                self.volume_name))
        else:
            logger.info("Create persistentvolumeclaim {} failed.".format(
                self.volume_name))
            self._update_volume_status(status='error')
            return None

        self._update_volume_status(status='active')

    def _create_volume_dir_on_nfs(self):
        """
        Create direction on nfs server to store volume data.
        """
        client = NFSLocalClient()
        client.removedir(self.nfs_path)
        client.makedir(self.nfs_path)
        return True

    def _create_persistentvolume(self):
        return self.kubeclient.create_persistentvolume(
            namespace=self.namespace,
            name=self.volume_name,
            capacity=self.capacity,
            nfs_path=self.nfs_path,
            nfs_server=self.nfs_server
            )

    def _create_persistentvolumeclaim(self):
        return self.kubeclient.create_persistentvolumeclaim(
            namespace=self.namespace,
            name=self.volume_name,
            capacity=self.capacity
            )

    def _update_volume_status(self, status):
        self.volume.status = status
        self.volume.save()


class VolumeDestroyer(object):
    """
    VolumeDestroyer is to destroy volume instance, including volume direction,
    persistentvolume and persistentvolumeclaim.
    """
    volume = None

    def __init__(self, volume):
        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))

        self.volume = volume
        self.namespace = self.volume.project.user.username
        self.project_name = self.volume.project.name
        self.volume_name = self.project_name + '-' + self.volume.name
        self.capacity = str(self.volume.capacity) + self.volume.capacity_unit
        self.nfs_path = get_volume_nfs_dir(settings.NFS_BASE_DIR,
            self.namespace, self.project_name, self.volume.name)
        self.nfs_server = settings.NFS_IP

    def destroy_volume(self):
        """
        Destroy volume instance by multiple threading.
        """
        deleting_thread = Thread(target=self._destroy_volume_instance)
        deleting_thread.start()

    def _destroy_volume_instance(self):
        logger.info('User {} delete volume {} in project {}.'.format(
            self.namespace, self.volume.name, self.project_name))

        self._update_volume_status(status='deleting')

        if not self._remove_volume_dir_on_nfs():
            logger.debug("remove direction {} on nfs server failed.".format(
                self.nfs_path))
        else:
            logger.info("remove direction {} on nfs server successfully."
                .format(self.nfs_path))

        if not self._delete_persistentvolumeclaim():
            logger.debug("delete persistentvolumeclaim {} failed.".format(
                self.volume_name))
        else:
            logger.debug("delete persistentvolumeclaim {} successfully."
                .format(self.volume_name))

        if not self._delete_persistentvolume():
            logger.debug("delete persistentvolume {}-{} failed.".format(
                self.namespace, self.volume_name))
        else:
            logger.debug("delete persistentvolume {}-{} successfully.".format(
                self.namespace, self.volume_name))

        # self._update_volume_status(status='deleted')
        self._delete_volume_metadata()

    def _remove_volume_dir_on_nfs(self):
        """
        Remove direction on nfs server.
        """
        client = NFSLocalClient()
        client.removedir(self.nfs_path)
        return True

    def _delete_persistentvolumeclaim(self):
        return self.kubeclient.delete_persistentvolumeclaim(
            namespace=self.namespace, name=self.volume_name)

    def _delete_persistentvolume(self):
        return self.kubeclient.delete_persistentvolume(
            namespace=self.namespace, name=self.volume_name)

    def _update_volume_status(self, status):
        self.volume.status = status
        self.volume.save()

    def _delete_volume_metadata(self):
        logger.debug("delete volume {} metadata.".format(self.volume_name))
        self.volume.delete()
