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
