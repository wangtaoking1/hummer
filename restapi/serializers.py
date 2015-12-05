from django.contrib.auth.models import User
from rest_framework import serializers

from restapi.models import MyUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ('url', 'username', 'email', 'is_staff', 'is_active')

