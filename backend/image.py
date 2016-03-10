import logging, json
from threading import Thread

from django.conf import settings
from docker import Client
from docker.errors import APIError

from backend.models import Image
from backend.utils import (fetch_digest_from_response, get_optimal_docker_host,
    remove_file_from_disk)
from backend.schedule import DockerSchedulerFactory

logger = logging.getLogger('hummer')


class ImageBuilder(object):
    """
    ImageBuilder is to build image. One way is to use image file directly, the
    other way is to use Dockerfile to build image.

    is_image: 0|1|2, 0 represents build file, 1 represents image file,
        2 represents container snapshot.
    """
    build_file = None
    is_image = 0
    dockerfile = None
    image = None
    user = None

    def __init__(self, build_file, is_image, dockerfile, image_id, user,
        old_image_name, old_image_version):
        self.build_file = build_file
        self.is_image = is_image
        self.dockerfile = dockerfile
        self.image = Image.objects.get(id=image_id)
        self.user = user
        self.old_image_name = old_image_name
        self.old_image_version = old_image_version

    def create_image(self):
        """
        Create image by two ways.
        """
        target = None
        if self.is_image != 0:
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

        docker_host = get_optimal_docker_host()
        if not docker_host:
            logger.error("there is no available active docker host.")
            self._update_image_status(status="failed")
            return None

        # TODO: create image on docker host
        base_url = self._get_docker_host_base_url(docker_host)
        image_name = self._get_image_name()

        if self.is_image == 1:
            token = self._load_image_on_docker_host(base_url, self.build_file,
                image_name, self.image.version)
        elif self.is_image == 2:
            token = self._import_snapshot_on_docker_host(base_url,
                self.build_file, image_name, self.image.version)

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
        logger.info('Image %s:%s has been pushed to registry, with digest %s',
            image_name, self.image.version, digest)

        self._update_image_status(status="active", digest=digest, token=token)

        remove_file_from_disk(self.build_file)

    def _create_image_by_dockerfile(self):
        """
        Create image by dockerfile, this maybe take a long time.
        """
        logger.debug("creating an image by dockerfile.")

        docker_host = get_optimal_docker_host()
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
        logger.info('Image %s:%s has been pushed to registry, with digest %s',
            image_name, self.image.version, digest)

        self._update_image_status(status="active", digest=digest, token=token)

        remove_file_from_disk(self.build_file)


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
        return '{}/{}/{}-{}'.format(settings.IMAGE_REGISTRY, self.user.username,
            self.image.project.name, self.image.name)

    def _load_image_on_docker_host(self, base_url, build_file, image_name,
                image_version='latest'):
        """
        Import container snapshot on the selected docker host.

        'base_url': the url of docker host.
        'build_file': the name of the build file in absolute path.
        'image_name': the name of the image, containing registry address, user
        name and image name.
        'image_version': the version of the image.

        Returns:
        'token': the image token
        """
        self._delete_image_on_docker_host(base_url, self.old_image_name,
            self.old_image_version)
        self._delete_image_on_docker_host(base_url, image_name, image_version)

        client = Client(base_url=base_url)
        try:
            with open(build_file, 'rb') as fileobj:
                client.load_image(fileobj)
        except Exception:
            logger.error('load image file on docker host %s failed.' % base_url)
            return None

        return self._tag_image_with_new_name(base_url, self.old_image_name,
            self.old_image_version, image_name, image_version)

    def _import_snapshot_on_docker_host(self, base_url, build_file, image_name,
                image_version='latest'):
        """
        Import container snapshot on the selected docker host.

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
            logger.error('import snapshot on docker host %s failed.' % base_url)
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
            client.remove_image(image=image_complete_name, force=True)
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
            logger.error('Parse the digest response error.')
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

    def _tag_image_with_new_name(self, base_url, old_image_name,
            old_image_version, image_name, image_version):
        """
        Docker tag old_image_name:old_image_version image_name:image_version.
        """
        client = Client(base_url=base_url)
        old_image = "{}:{}".format(old_image_name, old_image_version)
        try:
            response = client.tag(image=old_image, repository=image_name,
                tag=image_version)
        except Exception as e:
            logger.debug(e)
            response = False
        if not response:
            logger.info("Tag image {} to {}:{} failed.".format(old_image,
                image_name, image_version))
            return None

        image_token = self._get_image_token_on_docker_host(base_url,
            image_name, image_version)

        self._delete_image_on_docker_host(base_url, old_image_name,
            old_image_version)

        return image_token

    def _get_image_token_on_docker_host(self, base_url, image_name,
        image_version):
        """
        Given the image name and version, return the token of the image on the
        docker host.
        """
        image_complete_name = '%s:%s' %(image_name, image_version)

        logger.debug(image_complete_name)

        client = Client(base_url=base_url)
        try:
            images = client.images()
        except Exception as e:
            logger.debug(e)
            logger.debug("Communicate with docker host {} failed.".format(
                base_url))
            return None

        tokens = [image['Id'] for image in images
            if image_complete_name in image['RepoTags']]

        if not tokens:
            logger.info("The docker host {} has no image {}:{}".format(base_url,
                image_name, image_version))
            return None
        return tokens[0]

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
            logger.error('Cannot locate specified Dockerfile: %s.' %
                (self.dockerfile))
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


class ImageDestroyer(object):
    """
    ImageDestroyer is to destroy image instance by multiple threading.
    """
    image = None

    def __init__(self, image):
        self.image = image

    def destroy_image_instance(self):
        deleting_thread = Thread(target=self._destroy_image_instance)
        deleting_thread.start()

    def _destroy_image_instance(self):
        self._update_image_status(status='deleting')

        # TODO: delete the image instance

        self._delete_image_instance_on_all_hosts()
        self._delete_image_metadata()

    def _update_image_status(self, status):
        self.image.status = status
        self.image.save()

    def _delete_image_metadata(self):
        self.image.delete()

    def _delete_image_instance_on_all_hosts(self):
        """
        Delete image instance on all hosts.
        """
        image_name = self._get_image_name()
        image_version = self.image.version
        scheduler = DockerSchedulerFactory.get_scheduler()
        hosts = scheduler.get_docker_hosts()
        for host in hosts:
            base_url = self._get_docker_host_base_url(host)
            self._delete_image_on_docker_host(base_url, image_name,
                image_version)

    def _get_image_name(self):
        """
        Returns the complete name of the image.
        """
        return '{}/{}/{}-{}'.format(settings.IMAGE_REGISTRY,
            self.image.project.user.username,
            self.image.project.name, self.image.name)

    def _delete_image_on_docker_host(self, base_url, image_name, image_version):
        """
        Delete image from docker host if exists image called
        image_name:image_version.
        """
        image_complete_name = '%s:%s' %(image_name, image_version)
        client = Client(base_url=base_url)
        try:
            client.remove_image(image=image_complete_name, force=True)
        except Exception:
            logger.info('There is no image called %s on docker host %s' %
                (image_complete_name, base_url))
            return None

        logger.info('Image %s on docker host %s has been deleted.' %
                (image_complete_name, base_url))

    def _get_docker_host_base_url(self, host):
        """
        Returns the base url of docker host.
        """
        return 'tcp://%s:%s' % (host, str(settings.DOCKER_PORT))


class ImageCloner(object):
    """
    ImageCloner is to clone a public image into private project.
    """
    public_image = None
    private_image = None

    def __init__(self, puid, prid):
        self.public_image = Image.objects.get(id=puid)
        self.private_image = Image.objects.get(id=prid)

    def clone_image(self):
        """
        Clone public image into private project on docker host, and then repush
        to registry.
        """
        clone_thread = Thread(target=self._clone_public_image())
        clone_thread.start()

    def _clone_public_image(self):
        public_image_name = self._get_image_name(self.public_image)
        private_image_name = self._get_image_name(self.private_image)

        logger.debug("public image: {}:{}".format(public_image_name,
            self.public_image.version))
        logger.debug("private image: {}:{}".format(private_image_name,
            self.private_image.version))

        base_url = self._get_docker_host_base_url()
        if not base_url:
            logger.error("Clone public image {}:{} to {}:{} failed.".format(
                public_image_name, self.public_image.version,
                private_image_name, self.private_image.version))
            return None

        self._delete_image_on_docker_host(base_url, public_image_name,
            self.public_image.version)
        self._delete_image_on_docker_host(base_url, private_image_name,
            self.private_image.version)

        try:
            self._pull_image_to_docker_host(base_url, public_image_name,
                self.public_image.version)
        except Exception:
            logger.error("Pull image {}:{} from registry failed.".format(
                public_image_name, self.public_image.version))

        token = self._tag_image_with_new_name(base_url,
            public_image_name, self.public_image.version,
            private_image_name, self.private_image.version)
        if not token:
            logger.error("Clone public image {}:{} to {}:{} failed.".format(
                public_image_name, self.public_image.version,
                private_image_name, self.private_image.version))
            self._update_image_status(status="failed")
            return None

        digest = self._push_image_to_registry(base_url,
            private_image_name, self.private_image.version, token)
        if not digest:
            logger.error("Clone public image {}:{} to {}:{} failed.".format(
                public_image_name, self.public_image.version,
                private_image_name, self.private_image.version))
            self._update_image_status(status="failed")
            return None

        logger.info("Clone public image {}:{} to {}:{} successfully.".format(
                public_image_name, self.public_image.version,
                private_image_name, self.private_image.version))

        self._update_image_status(status="active", digest=digest, token=token)

    def _get_image_name(self, image):
        """
        Returns the complete name of the image in registry.
        """
        return '{}/{}/{}-{}'.format(settings.IMAGE_REGISTRY,
            image.project.user.username,
            image.project.name, image.name)

    def _get_docker_host_base_url(self):
        """
        Returns the optimal base url of docker host.
        """
        docker_host = get_optimal_docker_host()
        if not docker_host:
            logger.error("there is no available active docker host.")
            self._update_image_status(status="failed")
            return None
        return 'tcp://%s:%s' % (docker_host, str(settings.DOCKER_PORT))

    def _update_image_status(self, status, digest=None, token=None):
        """
        Update image metadata after clone the image.
        """
        self.private_image.status = status
        if digest:
            self.private_image.digest = digest
        if token:
            self.private_image.token = token
        self.private_image.save()

    def _delete_image_on_docker_host(self, base_url, image_name, image_version):
        """
        Delete image from docker host if exists image called
        image_name:image_version.
        """
        image_complete_name = '%s:%s' %(image_name, image_version)
        client = Client(base_url=base_url)
        try:
            client.remove_image(image=image_complete_name, force=True)
        except Exception:
            logger.info('There is no image called %s on docker host %s' %
                (image_complete_name, base_url))
            return None

        logger.info('Image %s on docker host %s has been deleted.' %
                (image_complete_name, base_url))

    def _pull_image_to_docker_host(self, base_url, image_name, image_version):
        """
        Pull image from private registry to docker host.
        """
        client = Client(base_url=base_url)
        response = [line for line in client.pull(repository=image_name,
                tag=image_version, stream=True)]

    def _tag_image_with_new_name(self, base_url, old_image_name,
            old_image_version, image_name, image_version):
        """
        Docker tag old_image_name:old_image_version image_name:image_version.
        """
        client = Client(base_url=base_url)
        old_image = "{}:{}".format(old_image_name, old_image_version)
        try:
            response = client.tag(image=old_image, repository=image_name,
                tag=image_version)
        except Exception as e:
            logger.debug(e)
            response = False
        if not response:
            logger.info("Tag image {} to {}:{} failed.".format(old_image,
                image_name, image_version))
            return None

        image_token = self._get_image_token_on_docker_host(base_url,
            image_name, image_version)

        self._delete_image_on_docker_host(base_url, old_image_name,
            old_image_version)

        return image_token

    def _push_image_to_registry(self, base_url, image_name, image_version,
        image_token):
        """
        Push image from docker host to private registry.

        Returns the sha256 digest of the image.
        """
        image_complete_name = '%s:%s' %(image_name, image_version)

        client = Client(base_url=base_url)
        try:
            response = [res for res in client.push(image_complete_name,
                stream=True)]
        except Exception:
            logger.error('Push image %s to registry failed.' %
                image_complete_name)
            return None

        try:
            digest = fetch_digest_from_response(response[-1])
        except Exception:
            logger.error('Parse the digest response error.')
            return None

        return digest

    def _get_image_token_on_docker_host(self, base_url, image_name,
        image_version):
        """
        Given the image name and version, return the token of the image on the
        docker host.
        """
        image_complete_name = '%s:%s' %(image_name, image_version)

        logger.debug(image_complete_name)

        client = Client(base_url=base_url)
        try:
            images = client.images()
        except Exception as e:
            logger.debug(e)
            logger.debug("Communicate with docker host {} failed.".format(
                base_url))
            return None

        tokens = [image['Id'] for image in images
            if image_complete_name in image['RepoTags']]

        if not tokens:
            logger.info("The docker host {} has no image {}:{}".format(base_url,
                image_name, image_version))
            return None
        return tokens[0]
