import logging
import random

import etcd
from django.conf import settings

logger = logging.getLogger('hummer')


class DockerScheduler(object):
    """
    DockerScheduler is a Docker Scheduler which is used to select a Docker
    mechine by a few strategies.
    """
    etcd_host = None
    etcd_port = None
    docker_hosts = None
    current_host = None

    def __init__(self, etcd_host='127.0.0.1', etcd_port=4001):
        self.etcd_host = etcd_host
        self.etcd_port = etcd_port
        self.docker_hosts = self._update_docker_list()

    def _update_docker_list(self):
        """
        Communicate with the etcd service, then update the docker list.
        """
        client = etcd.Client(host=self.etcd_host, port=self.etcd_port)
        try:
            result = client.get('/registry/minions/')
        except Exception:
            logger.error("Can't connect to etcd host %s:%s" % (self.etcd_host,
                self.etcd_port))
            return []

        hosts = []
        for child in result.children:
            hosts.append(child.key.split('/')[-1])
        return sorted(hosts)

    def get_docker_hosts(self):
        return self.docker_hosts

    def get_optimal_docker_host(self):
        """
        Returns the optimal docker host from the docker host lists by polling
        strategy.
        """
        self.docker_hosts = self._update_docker_list()
        if not self.docker_hosts:
            return None

        if (not self.current_host or
            (self.current_host not in self.docker_hosts)):
            index = random.randint(0, len(self.docker_hosts))
        else:
            index = self.docker_hosts.index(self.current_host)

        next_index = (index + 1) % len(self.docker_hosts)

        self.current_host = self.docker_hosts[next_index]

        return self.current_host


class DockerSchedulerFactory(object):
    """
    Factory of DockerScheduler, to use the only one scheduler allways.
    """
    _scheduler = None

    @classmethod
    def get_scheduler(self):
        if not self._scheduler:
            self._scheduler = DockerScheduler(settings.MASTER_IP,
                settings.ETCD_PORT)
        return self._scheduler
