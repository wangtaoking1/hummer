from rest_framework import serializers

from backend.models import MyUser, Project, Image, Application, Port


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('url', 'username', 'email', 'is_staff', 'is_active')


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('url', 'id', 'user', 'name', 'desc', 'create_time')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'project', 'name', 'desc', 'version', 'digest',
            'token', 'is_public', 'create_time', 'status')


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ('id', 'image', 'name', 'replicas', 'session_affinity', 'internal_ip',
            'external_ip', 'create_time', 'status')


class PortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Port
        fields = ('id', 'app', 'name', 'protocol', 'internal_port',
            'external_port')

