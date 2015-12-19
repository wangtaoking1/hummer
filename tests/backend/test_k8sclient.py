import unittest, json

from backend.k8sclient import KubeClient


class KubeClientTestCase(unittest.TestCase):
    def setUp(self):
        self.client = KubeClient("http://192.168.0.10:8080/api/v1/")

    def tearDown(self):
        self.client = None

    def test_add_slash(self):
        url = "http://192.168.0.10:8080"
        self.assertEqual(KubeClient.add_slash(url), "http://192.168.0.10:8080/")

    def test_create_instance(self):
        url = "http://192.168.0.10:8080"
        client = KubeClient(url)
        self.assertEqual(client.base_url, "http://192.168.0.10:8080/")

    def test_send_request(self):
        res = self.client.send_request("get", "namespaces", labels={'a': 1, 'name': 'wangtao'})
        self.assertEqual(isinstance(res, dict), True)

    def test_list_namespaces(self):
        namespaces = self.client.list_namespces()
        # print(namespaces)
        self.assertEqual(len(namespaces), 1)

    def test_list_nodes(self):

        nodes = self.client.list_nodes()
        print(nodes)
        self.assertEqual(len(nodes), 1)

    def test_create_namespace(self):
        self.client.create_namespace('abcd')
        res = self.client.list_namespces()
        print(res)
        self.assertEqual(len(res), len(res))

    def test_delete_namespace(self):
        before = len(self.client.list_namespces())
        self.client.delete_namespace('abcd')
        after = len(self.client.list_namespces())
        self.assertEqual(before, after + 1)
