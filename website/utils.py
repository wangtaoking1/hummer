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

