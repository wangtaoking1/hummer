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
from restapi.utils import (save_image_file_to_disk, is_image_or_dockerfile, get_upload_image_filename)
from backend.image import ImageBuilder, ImageDestroyer
from backend.application import ApplicationBuilder

logger = logging.getLogger("hummer")


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = (IsAdminUser,)


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

        data = request.data
        data['project'] = self.kwargs['pid']
        # create image metadata
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

        image = serializer.data
        logger.debug(image)

        is_image = is_image_or_dockerfile(request.data.get('is_image', 'true'))
        dockerfile = None
        if not is_image:
            dockerfile = request.data.get('dockerfile', 'Dockerfile')
        filename = get_upload_image_filename(image, request.user)

        save_image_file_to_disk(request.FILES['file'], filename)

        # create a true image instance, and upload into private registry
        builder = ImageBuilder(
            build_file=filename,
            is_image=is_image,
            dockerfile=dockerfile,
            image_id=image['id'],
            user=request.user
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

        # create application metadata
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = Response(serializer.data, status=status.HTTP_201_CREATED,
            headers=headers)

        application = serializer.data
        logger.debug(application)

        image_name = "{}/{}/{}:{}".format(settings.IMAGE_REGISTRY,
            request.user.username, image.name, image.version)
        logger.debug(image_name)
        # create a true application instance
        # build = ApplicationBuilder(
        #     namespace=request.user.username,
        #     application=application,
        #     image_name=image_name,
        #     tcp_ports, udp_ports, commands, args, envs, is_public)
        # builder = ImageBuilder(
        #     build_file=filename,
        #     is_image=is_image,
        #     dockerfile=dockerfile,
        #     image_id=image['id'],
        #     user=request.user
        #     )
        # builder.create_image()

        return response
