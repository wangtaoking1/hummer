import unittest

from backend.k8sclient import KubeClient


class KubeClientTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        self.client = None

    def test_create_image(self):
        pass

