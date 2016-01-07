import logging
import os

from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import (PermissionDenied, ValidationError,
    ParseError, NotFound)

from restapi.serializers import (UserSerializer, ProjectSerializer,
    ImageSerializer, ApplicationSerializer, PortSerializer,
    ResourceLimitSerializer, VolumeSerializer)
from backend.models import (MyUser, Project, Image, Application, Port,
    ResourceLimit, Volume)
from restapi.utils import (save_upload_file_to_disk, is_image_or_dockerfile, get_upload_image_filename, get_ports_by_protocol,
    get_upload_volume_filename, get_volume_direction_on_nfs,
    big_file_iterator)
from backend.image import (ImageBuilder, ImageDestroyer)
from backend.application import (ApplicationBuilder, ApplicationDestroyer)
from backend.volume import (VolumeBuilder, VolumeDestroyer)
from backend.kubernetes.k8sclient import KubeClient
from backend.nfs import NFSLocalClient
from backend.utils import (remove_file_from_disk)

logger = logging.getLogger("hummer")


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = (IsAdminUser,)

    def destroy(self, request, *args, **kwargs):
        """
        Destroy an user instance.
        """
        user = self.get_object()

        # Delete the namespace
        kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))

        kubeclient.delete_namespace(user.username)

        return super(UserViewSet, self).destroy(request, *args, **kwargs)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all the projects for the currently
        authenticated user.
        """
        user = self.request.user

        # AdminUser
        if user.is_staff:
            return Project.objects.all()

        return Project.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        user = self.request.user

        project = Project.objects.filter(user=user,
            name=request.data.get('name', None))
        if project:
            raise ValidationError(detail="Already has an project called {}."
                .format(request.data['name']))

        return super(ProjectViewSet, self).create(request, *args, **kwargs)

class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """
        This view should return a list of all the images for the current
        project.
        """
        user = self.request.user

        assert 'pid' in self.kwargs
        pid = self.kwargs['pid']
        if user.is_staff:
            return Image.objects.filter(project__id=pid)
        else:
            return Image.objects.filter(project__id=pid, project__user=user)

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        user = self.request.user

        assert 'pid' in self.kwargs
        pid = self.kwargs['pid']

        assert 'pk' in self.kwargs
        id = self.kwargs['pk']
        obj = Image.objects.get(project__id=pid, id=id)

        # Check user permission
        if not user.is_staff and user != obj.project.user:
            raise PermissionDenied()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        """
        Create an image instance.
        """
        logger.info("user %s will create a new image" % request.user.username)

        if not request.FILES.get('file'):
            raise ParseError(detail="There is no image build file.")

        assert 'pid' in self.kwargs
        pid = self.kwargs['pid']

        data = request.data
        data['project'] = pid
        # create image metadata
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        images = Image.objects.filter(project__id=pid, name=data['name'],
            version=data['version'])
        if images:
            raise ValidationError(detail="Already has an image called {}."
                .format(data['name']))

        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

        image = serializer.data
        logger.debug(image)

        is_image = is_image_or_dockerfile(request.data.get('is_image', None))
        dockerfile = None
        old_image_name = None
        old_image_version = None
        if is_image == 0:
            dockerfile = request.data.get('dockerfile', 'Dockerfile')
        if is_image == 1:
            old_image_name = request.data.get('old_image_name',
                image['name'])
            old_image_version = request.data.get('old_image_version',
                image['version'])

        filename = get_upload_image_filename(image, request.user)

        save_upload_file_to_disk(request.FILES['file'], filename)

        # create a true image instance, and upload into private registry
        builder = ImageBuilder(
            build_file=filename,
            is_image=is_image,
            dockerfile=dockerfile,
            image_id=image['id'],
            user=request.user,
            old_image_name=old_image_name,
            old_image_version=old_image_version
            )
        builder.create_image()

        return response

    def destroy(self, request, *args, **kwargs):
        """
        Destroy an image instance.
        """
        image = self.get_object()

        logger.info("user %s deletes image: %s/%s:%s" % (
            request.user.username,
            image.project.user.username,
            image.name,
            image.version))

        destroyer = ImageDestroyer(image)
        destroyer.destroy_image_instance()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        assert 'pid' in self.kwargs
        pid = self.kwargs['pid']
        if user.is_staff:
            return Application.objects.filter(image__project__id=pid)
        else:
            return Application.objects.filter(image__project__id=pid,
                image__project__user=user)

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        user = self.request.user

        assert 'pid' in self.kwargs
        pid = self.kwargs['pid']

        assert 'pk' in self.kwargs
        id = self.kwargs['pk']
        obj = Application.objects.get(image__project__id=pid, id=id)

        # Check user permission
        if not user.is_staff and user != obj.image.project.user:
            raise PermissionDenied()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        """
        Create an application instance.
        """
        user = request.user

        logger.info("user {} will create an application.".format(
            user.username))

        assert 'pid' in self.kwargs

        # Check whether image is corresponding to the project
        image_id = request.data.get('image', None)
        pid = int(self.kwargs['pid'])
        image = Image.objects.get(id=image_id)
        if not image or image.project.id != pid:
            raise NotFound(detail="Image {} isn't in project {}.".format(
                image_id, pid))

        # Check whether project is corresponding to the user
        project = Project.objects.get(id=pid)
        if not project or project.user != user:
            raise PermissionDenied()

        applications = Application.objects.filter(image__project=project,
            name=request.data.get('name'))
        if applications:
            raise ValidationError(detail="Already has an application called {}."
                .format(request.data.get('name')))

        volumes = request.data.get('volumes', [])
        for volume in volumes:
            volume = Volume.objects.get(id=volume['volume'])
            if volume.app or volume.mount_path:
                raise ValidationError(detail="Volume {} is being used by \
application {}.".format(volume.name, volume.app.name))

        # create application metadata
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

        application = Application.objects.get(id=serializer.data['id'])
        logger.debug(application)

        image_name = "{}/{}/{}-{}:{}".format(settings.IMAGE_REGISTRY,
            request.user.username, image.project.name, image.name, image.version)
        logger.debug(image_name)
        ports = request.data.get('ports', None)

        # create a true application instance
        builder = ApplicationBuilder(
            namespace=request.user.username,
            application=application,
            image_name=image_name,
            tcp_ports=get_ports_by_protocol('TCP', ports),
            udp_ports=get_ports_by_protocol('UDP', ports),
            commands=request.data.get('commands', None),
            args=request.data.get('args', None),
            envs=request.data.get('envs', None),
            is_public=request.data.get('is_public', False),
            volumes=request.data.get('volumes', None)
        )
        builder.create_application()

        return response

    def destroy(self, request, *args, **kwargs):
        """
        Destroy an application instance.
        """
        application = self.get_object()

        logger.info("user {} deletes application: {}.".format(
            request.user.username, application.name))

        destroyer = ApplicationDestroyer(application=application)
        destroyer.destroy_application_instance()

        return Response(status=status.HTTP_204_NO_CONTENT)

class PortViewSet(viewsets.ModelViewSet):
    serializer_class = PortSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        assert 'pid' in self.kwargs
        assert 'aid' in self.kwargs
        pid = self.kwargs['pid']
        aid = self.kwargs['aid']

        if user.is_staff:
            return Port.objects.filter(app__image__project__id=pid,
                app__id=aid)
        else:
            return Port.objects.filter(app__image__project__id=pid,
                app__id=aid, app__image__project__user=user)

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        user = self.request.user

        assert 'pid' in self.kwargs
        assert 'aid' in self.kwargs
        pid = self.kwargs['pid']
        aid = self.kwargs['aid']

        assert 'pk' in self.kwargs
        id = self.kwargs['pk']
        obj = Port.objects.get(app__image__project__id=pid, app__id=aid,
            id=id)

        # Check user permission
        if not user.is_staff and user != obj.app.image.project.user:
            raise PermissionDenied()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


class ResourceLimitViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceLimitSerializer
    queryset = ResourceLimit.objects.all()

    permission_classes = (IsAdminUser,)


class VolumeViewSet(viewsets.ModelViewSet):
    serializer_class = VolumeSerializer

    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        assert 'pid' in self.kwargs
        pid = self.kwargs['pid']

        if user.is_staff:
            return Volume.objects.filter(project__id=pid)
        else:
            return Volume.objects.filter(project__id=pid, project__user=user)

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        user = self.request.user

        assert 'pid' in self.kwargs
        pid = self.kwargs['pid']

        assert 'pk' in self.kwargs
        id = self.kwargs['pk']
        obj = Volume.objects.get(project__id=pid, id=id)

        # Check user permission
        if not user.is_staff and user != obj.project.user:
            raise PermissionDenied()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def create(self, request, *args, **kwargs):
        """
        Create an application instance.
        """
        user = request.user

        logger.info("user {} will create an volume.".format(
            user.username))

        assert 'pid' in self.kwargs
        pid = int(self.kwargs['pid'])

        # Check whether project is corresponding to the user
        project = Project.objects.get(id=pid)
        if not project or project.user != user:
            raise PermissionDenied()

        # Check whether or not exists the same name volume in the project
        volumes = Volume.objects.filter(project__id=pid,
            name=request.data.get('name', ''))
        if volumes:
            raise ValidationError(
                detail="Already has an volume called {} in this project."
                .format(request.data.get('name', '')))

        app = request.data.get('app', None)
        if app:
            raise ValidationError(detail="Shouldn't contain app attribute.")

        # create volume metadata
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

        volume = Volume.objects.get(id=serializer.data['id'])
        # logger.debug(volume)

        # create volume instance
        builder = VolumeBuilder(volume)
        builder.create_volume()

        return response

    def destroy(self, request, *args, **kwargs):
        """
        Destroy volume metadata and instance.
        """
        volume = self.get_object()

        if volume.app:
            raise ValidationError(detail="The volume is being used by \
application {}, delete the application first.".format(volume.app.name))

        # Delete the volume instance
        destroyer = VolumeDestroyer(volume=volume)
        destroyer.destroy_volume()

        return Response(status=status.HTTP_204_NO_CONTENT)

    def download(self, request, *args, **kwargs):
        """
        Download the volume data.
        """
        volume = self.get_object()

        logger.info("User {} download the data of volume {}-{}.".format(
            request.user.username, volume.project.name, volume.name))

        # Copy file to local first
        volume_dir = get_volume_direction_on_nfs(volume, request.user)
        filename = get_upload_volume_filename(volume, request.user)
        client = NFSLocalClient()
        client.tar_and_copy_to_local(volume_dir, filename)

        response = StreamingHttpResponse(big_file_iterator(filename))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(
            os.path.basename(filename))

        return response

    def upload(self, request, *args, **kwargs):
        """
        User upload volume data, delete the original data first.
        """
        volume = self.get_object()
        if not request.FILES.get('file'):
            raise ParseError(detail="There is no upload file.")

        logger.info("User {} upload files to volume {}-{}.".format(
            request.user.username, volume.project.name, volume.name))

        filename = get_upload_volume_filename(volume, request.user)
        save_upload_file_to_disk(request.FILES['file'], filename)

        client = NFSLocalClient()
        volume_dir = get_volume_direction_on_nfs(volume, request.user)
        # Clear the dir first
        client.removedir(volume_dir)
        client.makedir(volume_dir)

        client.copy_file_to_remote_and_untar(filename, volume_dir)
        remove_file_from_disk(filename)

        return Response(status=status.HTTP_202_ACCEPTED)
