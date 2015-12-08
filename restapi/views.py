from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from restapi.serializers import UserSerializer, AppSerializer, ImageSerializer
from restapi.models import MyUser, App, Image


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = (IsAdminUser,)


class AppViewSet(viewsets.ModelViewSet):
    queryset = App.objects.all()
    serializer_class = AppSerializer


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

