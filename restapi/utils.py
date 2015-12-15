import os
import logging

from django.conf import settings

logger = logging.getLogger('hummer')


def save_image_file_to_disk(file_obj, filename):
    """
    Save the image file into disk, then use it to build image.
    """
    image_dir = os.path.dirname(filename)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)

    with open(filename, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)


def is_image_or_dockerfile(is_image=None):
    """
    Parse the is_image option of the http data.
    'true' represents the image file is an image, 'false' represents the image
    file is a dockerfile used to build the image.
    """
    is_image = is_image.lower()
    if 'true' == is_image or '1' == is_image:
        return True
    return False


def get_upload_image_filename(image, user):
    """
    Return the filename of the uploaded image file in disk
    """
    filename = image['name'] + '_' + image['version'] + '.tar'
    return os.path.join(settings.UPLOAD_DIR, user.username, filename)

