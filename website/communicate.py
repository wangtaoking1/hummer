import requests
import json

from website.utils import (get_api_server_url)


class Communicator(object):
    """
    The Communicator with the backend api server.
    """
    client = None

    def __init__(self, cookies={}):
        self.client = requests.session()
        for name, value in cookies.items():
            self.client.cookies[name] = value

    def login(self, data):
        """
        Return cookies.
        """
        url = get_api_server_url('/api/auth/login/')
        self.client.get(url)
        data['csrfmiddlewaretoken'] = self.client.cookies['csrftoken']
        self.client.post(url, data)
        return dict(self.client.cookies)

    def logout(self):
        url = get_api_server_url('/api/auth/logout/')
        self.client.get(url)

        return dict(self.client.cookies)

    def is_authenticated(self):
        """
        Return (True, username) if authenticated, else return (False, None)
        """
        url = get_api_server_url('/api/auth/is_authenticated/')
        response = self.client.get(url)

        if response.status_code == 200:
            return True, json.loads(response.text)
        else:
            return False, None

    def registry(self, data):
        """
        User registry.
        """
        url = get_api_server_url('/api/users/')
        response = self.client.post(url, data)
        user_url = json.loads(response.text)['url']
        password_url = user_url + 'set_password/'
        self.client.post(password_url, data)

        return self.login(data)

    def project_lists(self):
        """
        Return the project lists of the user.
        """
        url = get_api_server_url('/api/projects/')
        response = self.client.get(url)
        return json.loads(response.text)


