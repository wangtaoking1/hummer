import logging, json
from threading import Thread

from django.conf import settings
from docker import Client
from docker.errors import APIError

from backend.models import Image
from backend.schedule import DockerSchedulerFactory
from backend.utils import (fetch_digest_from_response)

logger = logging.getLogger('hummer')


class ImageBuilder(object):
    """
    ImageBuilder is to build image. One way is to use image file directly, the
    other way is to use Dockerfile to build image.
    """
    build_file = None
    is_image = False
    dockerfile = None
    image = None
    user = None

    def __init__(self, build_file, is_image, dockerfile, image_id, user):
        self.build_file = build_file
        self.is_image = is_image
        self.dockerfile = dockerfile
        self.image = Image.objects.get(id=image_id)
        self.user = user

    def create_image(self):
        """
        Create image by two ways.
        """
        target = None
        if self.is_image:
            target = self._create_image_by_imagefile
        else:
            target = self._create_image_by_dockerfile

        creating_thread = Thread(target=target)
        creating_thread.start()

    def _create_image_by_imagefile(self):
        """
        Create image by imagefile.
        """
        logger.debug("creating an image by imagefile.")

        docker_host = self._get_build_docker_host()
        if not docker_host:
            logger.error("there is no available active docker host.")
            self._update_image_status(status="failed")
            return None

        # TODO: create image on docker host
        base_url = self._get_docker_host_base_url(docker_host)
        image_name = self._get_image_name()

        token = self._import_image_on_docker_host(base_url, self.build_file,
            image_name, self.image.version)
        if not token:
            logger.error("Import image on docker host failed")
            self._update_image_status(status="failed")
            return None
        logger.info('Image %s:%s has been imported, with token %s', image_name,
            self.image.version, token)

        digest = self._push_image_to_registry(base_url, image_name,
            self.image.version, token)
        if not digest:
            logger.error("Push image from docker host to registry failed")
            self._update_image_status(status="failed")
            return None
        logger.info('Image %s:%s has been pushed to registry, with digest %s', image_name,
            self.image.version, digest)

        self._update_image_status(status="active", digest=digest, token=token)

    def _create_image_by_dockerfile(self):
        """
        Create image by dockerfile, this maybe take a long time.
        """
        logger.debug("creating an image by dockerfile.")

        docker_host = self._get_build_docker_host()
        if not docker_host:
            logger.error("there is no available active docker host.")
            self._update_image_status(status="failed")
            return None

        base_url = self._get_docker_host_base_url(docker_host)
        image_name = self._get_image_name()

        logger.debug('%s %s' % (base_url, image_name))

        token = self._build_image_on_docker_host(
            base_url=base_url,
            build_file=self.build_file,
            dockerfile=self.dockerfile,
            image_name=image_name,
            image_version=self.image.version)
        if not token:
            logger.error("Build image on docker host failed")
            self._update_image_status(status="failed")
            return None
        logger.info('Image %s:%s has been builded, with token %s', image_name,
            self.image.version, token)

        digest = self._push_image_to_registry(base_url, image_name,
            self.image.version, token)
        if not digest:
            logger.error("Push image from docker host to registry failed")
            self._update_image_status(status="failed")
            return None
        logger.info('Image %s:%s has been pushed to registry, with digest %s', image_name,
            self.image.version, digest)

        self._update_image_status(status="active", digest=digest, token=token)


    def _update_image_status(self, status, digest=None, token=None):
        """
        Update image metadata after building the image.
        """
        self.image.status = status
        if digest:
            self.image.digest = digest
        if token:
            self.image.token = token
        self.image.save()

    def _get_build_docker_host(self):
        """
        Returns the optimal docker host to build image.
        """
        scheduler = DockerSchedulerFactory.get_scheduler()
        docker_host = scheduler.get_optimal_docker_host()
        logger.debug("select the optimal docher host %s" % docker_host)
        return docker_host

    def _get_docker_host_base_url(self, host):
        """
        Returns the base url of docker host.
        """
        return 'tcp://%s:%s' % (host, str(settings.DOCKER_PORT))

    def _get_image_name(self):
        """
        Returns the complete name of the build image.
        """
        return '%s/%s/%s' % (settings.IMAGE_REGISTRY, self.user.username,
            self.image.name)

    def _import_image_on_docker_host(self, base_url, build_file, image_name,
                image_version='latest'):
        """
        Import image on the selected docker host.

        'base_url': the url of docker host.
        'build_file': the name of the build file in absolute path.
        'image_name': the name of the image, containing registry address, user
        name and image name.
        'image_version': the version of the image.

        Returns:
        'token': the image token
        """
        self._delete_image_on_docker_host(base_url, image_name, image_version)

        client = Client(base_url=base_url)
        try:
            res_json = client.import_image_from_file(build_file, image_name,
                image_version)
            res = json.loads(res_json)
        except Exception:
            logger.error('import image on docker host %s failed.' % base_url)
            return None

        return res.get('status', None)

    def _delete_image_on_docker_host(self, base_url, image_name, image_version):
        """
        Delete image from docker host if exists image called
        image_name:image_version.
        """
        image_complete_name = '%s:%s' %(image_name, image_version)
        client = Client(base_url=base_url)
        try:
            client.remove_image(image=image_complete_name)
        except Exception:
            logger.info('There is no image called %s on docker host %s' %
                (image_complete_name, base_url))
            return None

        logger.info('Image %s on docker host %s has been deleted.' %
                (image_complete_name, base_url))

    def _push_image_to_registry(self, base_url, image_name, image_version,
        image_token):
        """
        Push image from docker host to private registry.

        Returns the sha256 digest of the image.
        """
        image_complete_name = '%s:%s' %(image_name, image_version)

        if not self._is_image_on_docker_host(base_url, image_token):
            logger.error('There is no image called %s on docker host %s' %
                (image_complete_name, base_url))
            return None

        client = Client(base_url=base_url)
        try:
            response = [res for res in client.push(image_complete_name,
                stream=True)]
        except Exception:
            logger.error('Communicate with %s failed.' % base_url)
            return None

        try:
            digest = fetch_digest_from_response(response[-1])
        except Exception:
            logger.error('Parse the response error.')
            return None

        return digest

    def _is_image_on_docker_host(self, base_url, image_token):
        """
        Check the image whether or not on docker host.
        """
        client = Client(base_url=base_url)
        try:
            response = client.images(quiet=True)
        except Exception:
            logger.error("Connected %s failed." % base_url)
            return False
        if image_token not in response:
            return False
        return True

    def _build_image_on_docker_host(self, base_url, build_file, dockerfile,
            image_name, image_version):
        """
        Build image on the selected docker host by Dockerfile.

        'base_url': the url of docker host.
        'build_file': the name of the build file in absolute path.
        'dockerfile': Dockerfile path in build_file.
        'image_name': the name of the image, containing registry address, user
        name and image name.
        'image_version': the version of the image.

        Returns:
        'token': the image token
        """
        self._delete_image_on_docker_host(base_url, image_name, image_version)

        client = Client(base_url=base_url)
        fileobj = open(build_file, 'rb')
        image_complete_name = '%s:%s' % (image_name, image_version)
        try:
            response = [line for line in client.build(
                fileobj=fileobj,
                custom_context=True,
                dockerfile=dockerfile,
                rm=True,
                tag=image_complete_name)]
        except APIError as error:
            logger.debug(error)
            logger.error('Cannot locate specified Dockerfile: %s.' % self.dockerfile)
            fileobj.close()
            return None
        except Exception as error:
            logger.debug(error)
            logger.error('Build image %s failed.' % image_complete_name)
            fileobj.close()
            return None
        fileobj.close()

        return self._get_image_token(base_url, image_complete_name)

    def _get_image_token(self, base_url, image_complete_name):
        """
        """
        client = Client(base_url=base_url)
        try:
            token = client.inspect_image(image_complete_name).get('Id', None)
        except Exception:
            logger.error('Can\'t get the token of image %s on docker host %s' %
                (image_complete_name, base_url))
            return None
        return token
