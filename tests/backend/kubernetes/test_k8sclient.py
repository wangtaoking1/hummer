import unittest, json

from backend.kubernetes.k8sclient import KubeClient


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
        res = self.client.send_request("get", "namespaces",
            labels={'a': 1, 'name': 'wangtao'})
        self.assertEqual(isinstance(res, dict), True)

    def test_list_namespaces(self):
        namespaces = self.client.list_namespces()
        print(namespaces)
        self.assertEqual(True, True)

    def test_list_nodes(self):
        nodes = self.client.list_nodes()
        print(nodes)
        self.assertEqual(True, True)

    def test_create_namespace(self):
        self.client.create_namespace('abcd')
        self.assertEqual(len(res), len(res))

    def test_delete_namespace(self):
        self.client.delete_namespace('abcd')
        self.assertEqual(True, True)

    def test_list_controllers(self):
        controllers = self.client.list_controllers('test-space')
        print(controllers)

    def test_create_controller_1(self):
        image_name = '192.168.0.10:5000/admin/nginx:1.9.9'
        self.client.create_controller('test-space', 'test-nginx', image_name,
            replicas=1, tcp_ports={"http": 80, "https": 443})

    def test_create_controller_2(self):
        image_name = '192.168.0.10:5000/admin/ubuntu:14.04'
        self.client.create_controller('test-space', 'test-env', image_name,
            replicas=1,
            commands=['sleep', '3600'],
            envs={"MYSQL": "192.168.0.100"}
        )

    def test_delete_controller(self):
        self.client.delete_controller('test-space', 'test-nginx')

    def test_list_services(self):
        services = self.client.list_services('test-space')
        print(services)

    def test_create_service_internal(self):
        self.client.create_service('test-space', 'nginx',
            tcp_ports={"http": 80},
            is_public=False
        )

    def test_create_service_external(self):
        self.client.create_service('test-space', 'test-nginx',
            tcp_ports={"http": 80, "https": 443}, is_public=True)

    def test_create_service_session(self):
        self.client.create_service('test-space', 'nginx',
            tcp_ports={"http": 80},
            is_public=True,
            session_affinity=True
        )

    def test_delete_service(self):
        self.client.delete_service('test-space', 'nginx')
