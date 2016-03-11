import os
import json
import logging
import random

from django.conf import settings

from backend.kubernetes.k8sclient import KubeClient
from backend.schedule import DockerSchedulerFactory

logger = logging.getLogger('hummer')


def fetch_digest_from_response(response):
    """
    Fetch the image digest from response when push image from docker host to
    private registry.
    """
    # logger.debug(response)
    res = json.loads(response.decode())
    items = res.get('status').split(' ')
    res = [item for item in items if item.startswith('sha256:')]
    digest = res[0].split(':')[-1]

    return digest


def get_optimal_docker_host():
    """
    Returns the optimal docker host to build image.
    """
    scheduler = DockerSchedulerFactory.get_scheduler()
    docker_host = scheduler.get_optimal_docker_host()
    return docker_host


def get_volume_nfs_dir(base_dir, namespace, project, volume):
    """
    Create the volume dir in nfs server.
    """
    return os.path.join(base_dir, namespace, project, volume)


def remove_file_from_disk(filename):
    """
    Delete the file from disk.
    """
    if os.path.exists(filename):
        os.remove(filename)


def get_application_instance_name(application):
    """
    Return the name of the application instance.
    """
    return "{}-{}".format(application.image.project.name, application.name)


def get_optimal_external_ip(namespace, app_name):
    """
    Return the optimal external ip from all host ips of the application.
    """
    kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))
    label = "app=" + app_name
    hosts = kubeclient.list_host_ips(namespace=namespace, label=label)
    # logger.debug(hosts)
    index = random.randint(0, len(hosts) - 1)
    return hosts[index]
