from rest_framework import serializers

from backend.models import MyUser, App, Image

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('url', 'username', 'email', 'is_staff', 'is_active')


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ('url', 'id', 'user', 'name', 'desc', 'source', 'create_time')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('url', 'id', 'app', 'name', 'desc', 'version', 'token',
            'is_public', 'create_time', 'status')


# class ControllerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Controller
#         fields = ('url', 'id', 'name', 'user', 'image', 'status', 'replicas',
#             'create_time')
