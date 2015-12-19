import unittest
import os

from backend.schedule import DockerScheduler, DockerSchedulerFactory

class DockerSchedulerTestCase(unittest.TestCase):

    def setUp(self):
        self.scheduler = DockerScheduler('192.168.0.10', 4001)

    def tearDown(self):
        self.scheduler = None

    def test_docker_hosts(self):
        hosts = self.scheduler.get_docker_hosts()
        self.assertEqual(2, len(hosts))
        self.assertListEqual(sorted(hosts), ['192.168.0.10', '192.168.0.14'])


class DockerSchedulerFactoryTestCase(unittest.TestCase):
    def test_scheduler_factory(self):
        scheduler1 = DockerSchedulerFactory.get_scheduler()
        scheduler2 = DockerSchedulerFactory.get_scheduler()
        self.assertEqual(scheduler1, scheduler2)


# if __name__ == '__main__':
#     unittest.main()
