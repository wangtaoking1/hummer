import unittest

from website.communicate import Communicator


class CommunicatorTestCase(unittest.TestCase):
    def test_login(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        cookies = client.login(data)
        print(cookies)

    def test_logout(self):
        cookies = {'sessionid': 't53iaqdoqyw5rx9f9i8yjv0xjsb04v67'}
        client = Communicator(cookies=cookies)
        cookies = client.logout()
        print(cookies)

    def test_is_authenticated(self):
        cookies = {'sessionid': 'fw7a2cn2ybklvbcszv9qj6316ass7c8'}
        client = Communicator(cookies=cookies)
        ok, username = client.is_authenticated()
        print(ok)
        print(username)

    def test_registry(self):
        data = {
            'username': 'test',
            'password': 'test123',
            'email': 'test@hummer.com',
            'is_staff': False,
            'is_active': True
        }
        client = Communicator()
        cookies = client.registry(data)
        print(cookies)

    def test_project_lists(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        client.login(data)
        projects = client.project_lists()
        print(projects)

    def test_delete_project(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        client.login(data)
        client.delete_project(11)

    def test_delete_image(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        client.login(data)
        client.delete_image(1, 2)

    def test_create_image(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        client.login(data)
        params = {
            'name': 'nginx-a',
            'version': '1.9.9',
            'desc': 'nginx',
            'is_public': 'false',
            'is_image': '1',
            'old_image_name': 'nginx',
            'old_image_version': '1.9.9'
        }
        buildfile = '/home/wangtao/images/nginx.tar'
        client.create_image(1, params, buildfile)

    def test_create_application(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        client.login(data)

        data = {
            'image': 1,
            'name': 'test-app',
            'replicas': 1,
            'resource_limit': 1,
            'is_public': True,
            'session_affinity': False,
            'ports': [{'name': 'http', 'port': 80, 'protocol': 'TCP'}],
        }
        client.create_application(1, data)

    def test_upload_to_volume(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        client.login(data)

        files = "/home/wangtao/hummer-test/buildfiles/myubuntu/myubuntu.tar"
        client.upload_to_volume(1, 5, files)

    def test_clear_volume(self):
        client = Communicator()
        data = {
            'username': 'user',
            'password': 'user123'
        }
        client.login(data)

        client.clear_volume(1, 5)
