import json
import logging

import requests

from website.utils import (get_api_server_url, get_url_of_monitor_iframe)

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
            data = json.loads(response.text)
            return True, data[0], data[1]
        else:
            return False, None, None

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
        # print(response.status_code)
        # print(response.text)
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

    def create_application(self, project_id, json_data):
        """
        Create an application in project project_id with data.
        """
        url = get_api_server_url('/api/projects/{}/applications/'.format(project_id))

        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, json=json_data, headers=headers)
        # print(response.status_code)
        # print(response.text)
        if response.status_code == 201:
            return True
        return False

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
        # print(res.status_code)
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

    def get_volume_of_application(self, project_id, app_id):
        """
        Return the volume lists mounted on the application with id app_id.
        """
        volume_lists = self.volume_lists(project_id)
        volumes = []
        for volume in volume_lists:
            if volume['app'] == int(app_id):
                volumes.append(volume)

        return volumes

    def create_volume(self, project_id, data):
        """
        Create an application in project project_id with data.
        """
        url = get_api_server_url('/api/projects/{}/volumes/'.format(project_id))

        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, data=data, headers=headers)
        # print(response.status_code)
        # print(response.text)
        if response.status_code == 201:
            return True
        return False

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
        # print(res.status_code)
        if res.status_code == 204:
            return True
        return False

    def get_resourcelimits(self):
        """
        Get the resource limits list.
        """
        url = get_api_server_url('/api/resourcelimits/')
        res = self.client.get(url)
        return json.loads(res.text)

    def get_resourcelimit(self, lid):
        """
        Get the resource limit with id lid.
        """
        url = get_api_server_url('/api/resourcelimits/{}/'.format(lid))
        res = self.client.get(url)
        return json.loads(res.text)

    def get_ports(self, project_id, application_id):
        """
        Get the port lists of app with application_id in project project_id.
        """
        url = get_api_server_url('/api/projects/{}/applications/{}/ports/'
            .format(project_id, application_id))
        res = self.client.get(url)
        return json.loads(res.text)

    def get_pods(self, project_id, application_id):
        """
        Get the pod lists of app with application_id in project project_id.
        """
        url = get_api_server_url('/api/projects/{}/applications/{}/pods/'
            .format(project_id, application_id))
        res = self.client.get(url)
        return json.loads(res.text)

    def get_pod_logs(self, project_id, pod_name, tail=20):
        """
        Get the tail n lines logs of pod named pod_name in project project_id.
        """
        url = get_api_server_url('/api/projects/{}/pods/{}/logs/'.format(
            project_id, pod_name))
        params = {'tail': tail}
        res = self.client.get(url, params=params)
        return json.loads(res.text)

    def upload_to_volume(self, project_id, volume_id, fileobj):
        """
        Upload data into volume.
        """
        url = get_api_server_url('/api/projects/{}/volumes/{}/upload/'.format(
            project_id, volume_id))

        files = {'file': fileobj}
        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, files=files, headers=headers)
        # print(response.status_code)
        # print(response.text)
        if response.status_code == 200:
            return True
        return False

    def download_from_volume(self, project_id, volume_id):
        """
        Download data from volume with id volume_id.
        """
        url = get_api_server_url('/api/projects/{}/volumes/{}/download/'
            .format(project_id, volume_id))
        response = self.client.get(url)
        return response

    def clear_volume(self, project_id, volume_id):
        """
        Clear data of volume with id volume_id.
        """
        url = get_api_server_url('/api/projects/{}/volumes/{}/clear/'
            .format(project_id, volume_id))
        response = self.client.get(url)
        if response.status_code == 200:
            return True
        else:
            return False

    def get_container_monitor_image(self, type, namespace, pod_name):
        """
        Get container monitor image.

        Params:
        type: 1 is mem, 14 is cpu.
        """
        url = get_url_of_monitor_iframe(type, namespace, pod_name)
        response = self.client.get(url)
        return response

    def get_public_images(self):
        """
        Get public images.
        """
        url = get_api_server_url('/api/publics/')
        response = self.client.get(url)
        return json.loads(response.text)

    def get_public_image(self, public_id):
        url = get_api_server_url('/api/publics/{}/'.format(public_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def clone_public_image(self, public_id, data):
        """
        Clone public image into private registry.
        """
        url = get_api_server_url('/api/publics/{}/clone/'.format(public_id))

        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, data=data, headers=headers)
        # print(response.status_code)
        # print(response.text)
        if response.status_code == 201:
            return True
        return False

    def list_users(self):
        """
        Get user lists only for admin user.
        """
        url = get_api_server_url('/api/users/')
        response = self.client.get(url)
        return json.loads(response.text)

    def list_members(self, project_id):
        """
        List all members of project with id project_id.
        """
        url = get_api_server_url('/api/projects/{}/members/'.format(
            project_id))
        response = self.client.get(url)
        users = json.loads(response.text)
        members = []
        for user in users:
            member = {}
            member['id'] = user['pk']
            member['username'] = user['fields']['username']
            member['email'] = user['fields']['email']
            member['is_staff'] = user['fields']['is_staff']
            members.append(member)
        return members

    def list_resource_modules(self):
        """
        Return resource modules only for admin user.
        """
        url = get_api_server_url('/api/resourcelimits/')
        response = self.client.get(url)
        return json.loads(response.text)

    def delete_resource_module(self, module_id):
        url = get_api_server_url('/api/resourcelimits/{}/'.format(module_id))
        headers = {'X-CSRFToken': self.client.cookies['csrftoken']}
        res = self.client.delete(url, headers=headers)
        # print(res.status_code)
        if res.status_code == 204:
            return True
        return False

    def create_resource_module(self, data):
        """
        Create an resource module.
        """
        url = get_api_server_url('/api/resourcelimits/')

        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, data=data, headers=headers)
        # print(response.status_code)
        # print(response.text)
        if response.status_code == 201:
            return True
        return False

    def list_hosts(self):
        """
        List all hosts.
        """
        url = get_api_server_url('/api/hosts/')
        response = self.client.get(url)
        return json.loads(response.text)

    def list_projects_for_user(self, user_id):
        """
        List all projects for user with user_id.
        """
        url = get_api_server_url('/api/list-projects')
        params = {'user': user_id}

        response = self.client.get(url, params=params)
        return json.loads(response.text)

    def list_apps_for_project(self, project_id):
        """
        List all apps for project with project_id.
        """
        url = get_api_server_url('/api/list-apps')
        params = {'project': project_id}

        response = self.client.get(url, params=params)
        return json.loads(response.text)

    def list_pods_for_app(self, app_id):
        """
        List all pods for app with app_id.
        """
        url = get_api_server_url('/api/list-pods')
        params = {'app': app_id}

        response = self.client.get(url, params=params)
        return json.loads(response.text)

    def get_autoscaler(self, project_id, application_id):
        """
        Get autoscaler of application with id application_id.
        """
        url = get_api_server_url('/api/projects/{}/applications/{}/scalers/'
            .format(project_id, application_id))
        response = self.client.get(url)
        scalers = json.loads(response.text)
        if scalers:
            return scalers[0]
        return {}

    def get_environments(self, project_id, application_id):
        """
        Get environments of application with id application_id.
        """
        url = get_api_server_url('/api/projects/{}/applications/{}/envs/'
            .format(project_id, application_id))
        response = self.client.get(url)
        return json.loads(response.text)

    def add_members(self, project_id, users):
        """
        Add members to project with project_id.
        """
        url = get_api_server_url('/api/projects/{}/add_users/'
            .format(project_id))
        data = {
            'users': users
        }
        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return True
        return False

    def remove_members(self, project_id, users):
        """
        Remove members from project with project_id.
        """
        url = get_api_server_url('/api/projects/{}/remove_users/'
            .format(project_id))
        data = {
            'users': users
        }
        headers = {
            'X-CSRFToken': self.client.cookies['csrftoken'],
        }
        response = self.client.post(url, json=data, headers=headers)
        if response.status_code == 200:
            return True
        return False



