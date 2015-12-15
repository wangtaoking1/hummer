import os
import logging

from django.conf import settings

logger = logging.getLogger('hummer')


def save_image_file_to_disk(file_obj, username, filename):
    image_dir = os.path.join(settings.UPLOAD_DIR, username)
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    filename = os.path.join(image_dir, file_obj.name)

    with open(filename, 'wb+') as destination:
        for chunk in file_obj.chunks():
            destination.write(chunk)


