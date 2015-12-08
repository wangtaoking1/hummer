from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)


class MyUserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        return self._create_user(username, email, password, **extra_fields)


class MyUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=254, unique=True, db_index=True)
    email = models.EmailField('email address', max_length=254)

    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = MyUserManager()

    class Meta:
        # db_table = 'myuser'
        pass

    def get_full_name(self):
        return self.username

    def get_short_name(self):
        return self.username


class App(models.Model):
    """
    Each User has many projects called app, each app also contains one or more
    images.

    source represents the app which is　the current app cloned from, default null
     represents the app is a raw app.
    """
    source = models.ForeignKey('self', blank=True, null=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    name = models.CharField(max_length=128)
    desc = models.TextField(max_length=254, null=True)
    create_time = models.DateTimeField(auto_now=True)


class Image(models.Model):
    """
    Image represents the model of every Controller, and there are many different
    version images in every app.
    """
    STATUS_CHOICES = (
        ('deleted', 'deleted'),
        ('deleting', 'deleting'),
        ('active', 'active'),
        ('creating', 'creating'),
    )

    app = models.ForeignKey(App, on_delete=models.CASCADE)

    name = models.CharField(max_length=128)
    desc = models.TextField(max_length=254, null=True)
    version = models.CharField(max_length=32)
    token = models.CharField(max_length=64)
    is_public = models.BooleanField('public', default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
        default='creating')
    create_time = models.DateTimeField(auto_now=True)


# class Controller(models.Model):
#     """
#     Controller represents the running app, which maybe contains a few
#     containers, we can also open a service for controller.
#     """
#     STATUS_CHOICES = (
#         ('down', 'down'),
#         ('up', 'up'),
#         ('error', 'error'),
#     )

#     user = models.ForeignKey(MyUser, on_delete=models.CASCADE)
#     image = models.ForeignKey(Image, on_delete=models.SET_NULL, blank=True,
#         null=True)

#     name = models.CharField(max_length=128)
#     replicas = models.IntegerField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES)
#     create_time = models.DateTimeField(auto_now=True)

