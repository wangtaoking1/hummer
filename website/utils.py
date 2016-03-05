import os
from django.conf import settings


def get_api_server_url(path):
    """
    Return the url for api server.
    """
    return "http://" + settings.API_SERVER + path


def save_buildfile_to_disk(file_obj, project_id):
    """
    Save the upload file into directory with project_id on disk.
    """
    filename = get_filename_of_buildfile(project_id)
    file_dir = os.path.dirname(filename)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(filename, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)


def get_filename_of_buildfile(project_id):
    return os.path.join(settings.FILE_DIR, "buildfiles",
        project_id + ".tar")


# Get params from request.POST
def get_envs(number, data):
    envs = {}
    for i in range(number):
        key = 'env_name_' + str(i)
        val = 'env_value_' + str(i)
        envs[data[key]] = data[val]
    return envs

def get_ports(number, data):
    ports = []
    for i in range(number):
        port = {}
        port['name'] = data['port_name_' + str(i)]
        port['port'] = int(data['port_value_' + str(i)])
        port['protocol'] = data['port_protocol_' + str(i)]
        ports.append(port)
    return ports

def get_volumes(number, data):
    volumes = []
    for i in range(number):
        volume = {}
        volume['volume'] = int(data['volume_name_' + str(i)])
        volume['mount_path'] = data['volume_path_' + str(i)]
        volumes.append(volume)
    return volumes


def get_filename_of_volume_data(volume_id):
    return os.path.join(settings.FILE_DIR, "volumes",
        volume_id + ".tar")


def save_volume_data_to_disk(file_obj, volume_id):
    """
    Save the upload volume data into directory with volume_id on disk.
    """
    filename = get_filename_of_volume_data(volume_id)
    file_dir = os.path.dirname(filename)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(filename, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)


def get_url_of_monitor_iframe(type, namespace, pod_name):
    """
    Get the url of monitor iframe in user dashboard.
    """
    if type == "memory":
        type_id = 1
    elif type == "cpu":
        type_id = 14

    items = pod_name.split('-')
    container = '-'.join(items[0:-1])
    url = 'http://{}/dashboard-solo/db/containers?panelId={}&fullscreen&\
var-namespace={}&var-pod={}&var-container={}'.format(settings.GRAFANA_SERVER,
    type_id, namespace, pod_name, container)

    return url


def get_url_of_host_monitor(type, host):
    """
    Get the url of host monitor in admin dashboard.
    """
    panel_ids = {
        "all": {
            "memory": 15,
            "cpu": 11,
            "disk": 19
        },
        "node": {
            "memory": 7,
            "disk": 10,
            "cpu": 16
        }
    }

    if host == "All Hosts":
        type_id = panel_ids['all'][type]
    else:
        type_id = panel_ids['node'][type]

    url = 'http://{}/dashboard-solo/db/kubernetes-cluster?panelId={}&\
fullscreen'.format(settings.GRAFANA_SERVER, type_id)
    if host != "All Hosts":
        url += '&var-node={}'.format(host)
    return url


