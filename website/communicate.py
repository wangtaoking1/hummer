import json
import logging

import requests

from website.utils import (get_api_server_url)

logger = logging.getLogger('website')


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
        return self.client.cookies

    def logout(self):
        url = get_api_server_url('/api/auth/logout/')
        self.client.get(url)

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

    def create_project(self, data):
        """
        Create an project for user.
        """
        url = get_api_server_url('/api/projects/')
        response = self.client.post(url, data)
        if response.status_code == 201:
            return True
        return False

    def delete_project(self, project_id):
        """
        Delete the project with id project_id.
        """
        url = get_api_server_url('/api/projects/{}/'.format(project_id))
        headers = {'X-CSRFToken': self.client.cookies['csrftoken']}
        res = self.client.delete(url, headers=headers)
        if res.status_code == 204:
            return True
        return False

    def get_project(self, project_id):
        """
        Get the detail info of the project.
        """
        url = get_api_server_url('/api/projects/{}/'.format(project_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def image_lists(self, project_id):
        """
        Return the image lists of the project.
        """
        url = get_api_server_url('/api/projects/{}/images/'.format(project_id))
        response = self.client.get(url)
        return json.loads(response.text)


    def create_image(self, project_id, data, buildfile):
        """
        Create an image in project project_id with data and buildfile.
        """
        url = get_api_server_url('/api/projects/{}/create_image/'.format(project_id))

        files = {'file': open(buildfile, 'rb')}
        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, data=data, files=files,
            headers=headers)
        print(response.status_code)
        print(response.text)
        if response.status_code == 200:
            return True
        return False

    def get_image(self, project_id, image_id):
        """
        Get the detail info of the image.
        """
        url = get_api_server_url('/api/projects/{}/images/{}/'.format(
            project_id, image_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def delete_image(self, project_id, image_id):
        """
        Delete the image in the project.
        """
        url = get_api_server_url('/api/projects/{}/images/{}/'.format(
            project_id, image_id))
        headers = {'X-CSRFToken': self.client.cookies['csrftoken']}
        res = self.client.delete(url, headers=headers)
        # print(res.status_code)
        if res.status_code == 204:
            return True
        return False

    def application_lists(self, project_id):
        """
        Return the application lists of the project.
        """
        url = get_api_server_url('/api/projects/{}/applications/'.format(project_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def get_application(self, project_id, application_id):
        """
        Get the detail info of the application.
        """
        url = get_api_server_url('/api/projects/{}/applications/{}/'.format(
            project_id, application_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def delete_application(self, project_id, application_id):
        """
        Delete the application in the project.
        """
        url = get_api_server_url('/api/projects/{}/applications/{}/'.format(
            project_id, application_id))
        headers = {'X-CSRFToken': self.client.cookies['csrftoken']}
        res = self.client.delete(url, headers=headers)
        print(res.status_code)
        if res.status_code == 204:
            return True
        return False

    def volume_lists(self, project_id):
        """
        Return the volume lists of the project.
        """
        url = get_api_server_url('/api/projects/{}/volumes/'.format(project_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def get_volume(self, project_id, volume_id):
        """
        Get the detail info of the volume.
        """
        url = get_api_server_url('/api/projects/{}/volumes/{}/'.format(
            project_id, volume_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def delete_volume(self, project_id, volume_id):
        """
        Delete the volume in the project.
        """
        url = get_api_server_url('/api/projects/{}/volumes/{}/'.format(
            project_id, volume_id))
        headers = {'X-CSRFToken': self.client.cookies['csrftoken']}
        res = self.client.delete(url, headers=headers)
        print(res.status_code)
        if res.status_code == 204:
            return True
        return False
