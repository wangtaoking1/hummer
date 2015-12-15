import logging
from threading import Thread

from backend.models import Image
from backend.schedule import DockerSchedulerFactory

logger = logging.getLogger('hummer')


class ImageBuilder(object):
    """
    ImageBuilder is to build image. One way is to use image file directly, the
    other way is to use Dockerfile to build image.
    """
    build_file = None
    is_image = False
    image = None
    user = None

    def __init__(self, build_file, is_image, image_id, user):
        self.build_file = build_file
        self.is_image = is_image
        self.image = Image.objects.get(id=image_id)
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

        scheduler = DockerSchedulerFactory.get_scheduler()
        docker_host = scheduler.get_optimal_docker_host()

        logger.debug("image is building on docher host %s" % docker_host)

        if not docker_host:
            self._update_image_status("failed")
            return

        # TODO: create image on docker host
        #
        self._update_image_status("active", "99998888")


    def _create_image_by_dockerfile(self):
        """
        Create image by dockerfile, this maybe take a long time.
        """
        logger.debug("creating an image by dockerfile.")
        pass

    def _update_image_status(self, status, token=None):
        """
        Update image metadata after building the image.
        """
        self.image.status = status
        self.image.token = token
        self.image.save()
