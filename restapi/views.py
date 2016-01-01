import logging
import os

from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from restapi.serializers import (UserSerializer, ProjectSerializer,
    ImageSerializer, ApplicationSerializer, PortSerializer)
from backend.models import MyUser, Project, Image, Application, Port
from restapi.utils import (save_image_file_to_disk, is_image_or_dockerfile, get_upload_image_filename, get_ports_by_protocol)
from backend.image import ImageBuilder, ImageDestroyer
from backend.application import ApplicationBuilder, ApplicationDestroy
from backend.kubernetes.k8sclient import KubeClient

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
        # AnonymousUser
        if not user.is_authenticated():
            raise PermissionDenied()

        # AdminUser
        if user.is_staff:
            return Project.objects.all()

        return Project.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        user = self.request.user

        project = Project.objects.filter(user=user,
            name=request.data.get('name', None))
        if project:
            raise Exception("Already has an project called {}."
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
            raise Exception("There is no image build file.")

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
            raise Exception("Already has an image called {}."
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

        save_image_file_to_disk(request.FILES['file'], filename)

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
            raise Exception("Image {} isn't in project {}.".format(
                image_id, pid))

        # Check whether project is corresponding to the user
        project = Project.objects.get(id=pid)
        if not project or project.user != user:
            raise Exception("User {} doesn't have project {}".format(
                user.username, pid))

        applications = Application.objects.filter(image__project=project,
            name=request.data.get('name'))
        if applications:
            raise Exception("Already has an application called {}."
                .format(request.data.get('name')))

        # create application metadata
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

        application = Application.objects.get(id=serializer.data['id'])
        logger.debug(application)

        image_name = "{}/{}/{}:{}".format(settings.IMAGE_REGISTRY,
            request.user.username, image.name, image.version)
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
            is_public=request.data.get('is_public', False)
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

        destroyer = ApplicationDestroy(application=application)
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
