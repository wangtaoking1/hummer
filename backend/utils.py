import os, json
import logging

from backend.schedule import DockerSchedulerFactory

logger = logging.getLogger('hummer')


def fetch_digest_from_response(response):
    """
    Fetch the image digest from response when push image from docker host to
    private registry.
    """
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
