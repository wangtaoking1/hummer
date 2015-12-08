from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import PermissionDenied

from restapi.serializers import UserSerializer, AppSerializer, ImageSerializer
from backend.models import MyUser, App, Image


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = UserSerializer

    permission_classes = (IsAdminUser,)


class AppViewSet(viewsets.ModelViewSet):
    serializer_class = AppSerializer

    def get_queryset(self):
        """
        This view should return a list of all the apps for the currently
        authenticated user.
        """
        user = self.request.user
        # AnonymousUser
        if not user.is_authenticated():
            raise PermissionDenied()

        # AdminUser
        if user.is_staff:
            return App.objects.filter()

        return App.objects.filter(user=user)


class ImageViewSet(viewsets.ModelViewSet):
    serializer_class = ImageSerializer

    def get_queryset(self):
        """
        This view should return a list of all the images for the current user.
        """
        user = self.request.user

        # AnonymousUser
        check_Anonymous(user)

        # Search by app_id, return the list of images for the current app
        app_id = self.request.query_params.get('app_id', None)
        if app_id is not None:
            app = App.objects.get(id=app_id)
            if app is not None and app.user == user or user.is_staff:
                return Image.objects.filter(app__id=app_id)
            raise PermissionDenied()

        # AdminUser
        if user.is_staff:
            return Image.objects.all()

        return Image.objects.filter(app__user=user)


    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        user = self.request.user
        # AnonymousUser
        check_Anonymous(user)

        lookup_url_kwarg = 'pk'
        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        id = self.kwargs[lookup_url_kwarg]
        obj = Image.objects.get(id=id)

        # Check user permission
        if not user.is_staff and user != obj.app.user:
            raise PermissionDenied()

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj


def check_Anonymous(user):
    """
    if the user is anonymous, raise PermissionDenied exception.
    """
    if not user.is_authenticated():
        raise PermissionDenied()
