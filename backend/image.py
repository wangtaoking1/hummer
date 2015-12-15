import logging
from threading import Thread

logger = logging.getLogger('hummer')


class ImageBuilder(object):
    """
    ImageBuilder is to build image. One way is to use image file directly, the
    other way is to use Dockerfile to build image.
    """
    build_file = None
    is_image = False
    image_id = None
    user = None

    def __init__(self, build_file, is_image, image_id, user):
        self.build_file = build_file
        self.is_image = is_image
        self.image_id = image_id
        self.user = user

    def create_image(self):
        """
        Create image by two ways.
        """
        target = None
        if self.is_image:
            target = self._create_image_by_imagefile()
        else:
            target = self._create_image_by_dockerfile()

        creating_thread = Thread(target=target)
        creating_thread.start()

    def _create_image_by_imagefile(self):
        """
        Create image by imagefile.
        """
        logger.debug("creating an image by imagefile.")

    def _create_image_by_dockerfile(self):
        """
        Create image by dockerfile, this maybe take a long time.
        """
        logger.debug("creating an image by dockerfile.")
