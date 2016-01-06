import os
import logging

from django.conf import settings

logger = logging.getLogger('hummer')


def save_upload_file_to_disk(file_obj, filename):
    """
    Save the upload file into disk.
    """
    file_dir = os.path.dirname(filename)
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(filename, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)


def is_image_or_dockerfile(is_image=None):
    """
    Parse the is_image option of the http data.
    1 represents the image file is an image, 0 represents the image
    file is a dockerfile used to build the image, 2 represents the container
    snapshot.
    """
    if not is_image:
        return 0
    if is_image == '1':
        return 1
    elif is_image == '2':
        return 2
    return 0


def get_upload_image_filename(image, user):
    """
    Return the filename of the uploaded image file in disk
    """
    filename = image['name'] + '_' + image['version'] + '.tar'
    return os.path.join(settings.FILE_DIR, user.username, 'images', filename)


def get_upload_volume_filename(volume, user):
    """
    Return the filename of the uploaded volume file in disk.
    """
    filename = volume.name + '.tar'
    return os.path.join(settings.FILE_DIR, user.username, 'volumes',
        volume.project.name, filename)


def get_volume_direction_on_nfs(volume, user):
    """
    Return the direction of the uploaded volume file on nfs.
    """
    return os.path.join(settings.NFS_BASE_DIR, user.username,
        volume.project.name, volume.name)


def get_ports_by_protocol(protocol, ports):
    """
    Get tcp or udp ports from the list of POST data.
    """
    result_ports = {}
    for port in ports:
        if port['protocol'] == protocol:
            result_ports[port['name']] = port['port']
    return result_ports


def big_file_iterator(filename, chunk_size=512):
    """
    Used to download big file.
    """
    with open(filename, 'rb') as f:
        while True:
            content = f.read(chunk_size)
            if content:
                yield content
            else:
                break

