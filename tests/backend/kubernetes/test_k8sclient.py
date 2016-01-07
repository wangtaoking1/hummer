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
        self.client.create_namespace('user')

    def test_delete_namespace(self):
        self.client.delete_namespace('abcd')

    def test_list_controllers(self):
        controllers = self.client.list_controllers('test-space')
        print(controllers)

    def test_create_controller_1(self):
        image_name = '192.168.0.15:5000/user/nginx:1.9.9'
        res = self.client.create_controller('user', 'test-nginx', image_name,
            replicas=2, tcp_ports={"http": 80})
        print(res)

    def test_create_controller_2(self):
        image_name = '192.168.0.15:5000/admin/ubuntu:14.04'
        self.client.create_controller('test-space', 'test-nginx', image_name,
            replicas=1,
            commands=['sleep', '3600'],
            envs={"MYSQL": "192.168.0.100"}
        )

    def test_create_controller_3(self):
        image_name = '192.168.0.15:5000/admin/nginx:1.9.9'
        self.client.create_controller('test-space', 'test-nginx', image_name,
            replicas=1, tcp_ports={"http": 80, "https": 443})

    def test_create_controller_volume(self):
        image_name = '192.168.0.15:5000/user/nginx:1.9.9'
        self.client.create_controller('user', 'test-nginx', image_name,
            cpu="100m", memory="64Mi", replicas=1, tcp_ports={"http": 80},
            volumes={"project0-volume0": "/var/www/html"})

    def test_delete_controller(self):
        self.client.delete_controller('test-space', 'test-nginx')

    def test_list_services(self):
        services = self.client.list_services('test-space')
        print(services)

    def test_create_service_internal(self):
        res = self.client.create_service('user', 'test-nginx',
            tcp_ports={"http": 80},
            is_public=False
        )
        print(res)

    def test_create_service_external(self):
        res = self.client.create_service('test-space', 'test-nginx',
            tcp_ports={"http": 80},
            is_public=True
        )
        print(res)

    def test_create_service_session(self):
        self.client.create_service('test-space', 'nginx',
            tcp_ports={"http": 80},
            is_public=True,
            session_affinity=True
        )

    def test_delete_service(self):
        self.client.delete_service('test-space', 'nginx')

    def test_get_service_details(self):
        res = self.client.get_service_details('test-space', 'test-nginx')
        print(res)

    def test_create_persistentvolume(self):
        res = self.client.create_persistentvolume('default', 'project0-volume0', '10Mi',
            '/hummer/user/project0/volume0', '192.168.0.15')
        print(res)

    def test_delete_persistentvolume(self):
        res = self.client.delete_persistentvolume('default', 'project0-volume0')
        print(res)

    def test_create_persistentvolumeclaim(self):
        res = self.client.create_persistentvolumeclaim('default', 'project0-volume0',
            '10Mi')
        print(res)

    def test_delete_persistentvolumeclaim(self):
        res = self.client.delete_persistentvolumeclaim('default', 'project0-volume0')
        print(res)
