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
    logger.debug("select the optimal docher host %s" % docker_host)
    return docker_host
