from django.conf import settings
from django.db import models
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin)

from backend.kubernetes.k8sclient import KubeClient


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
    username = models.CharField(max_length=32, unique=True, db_index=True)
    email = models.EmailField('email address', max_length=256)

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


class Project(models.Model):
    """
    Each User has many projects called project, each project also contains one
    or more images.
    """
    name = models.CharField(max_length=32, default='')
    desc = models.TextField(max_length=256, null=True)
    create_time = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(MyUser, blank=True)


class Image(models.Model):
    """
    Image represents the model of every application, and there are many
    different version images in every application.
    """
    STATUS_CHOICES = (
        ('deleted', 'deleted'),
        ('deleting', 'deleting'),
        ('active', 'active'),
        ('creating', 'creating'),
        ('failed', 'failed')
    )

    user = models.ForeignKey(MyUser,  on_delete=models.CASCADE, null=True,
        default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True,
        default=True)

    name = models.CharField(max_length=32, default='')
    desc = models.TextField(max_length=256, null=True)
    version = models.CharField(max_length=32)
    digest = models.CharField(max_length=64, blank=True, null=True, default='')
    token = models.CharField(max_length=64, blank=True, null=True, default='')
    is_public = models.BooleanField(default=False)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES,
        default='creating')
    create_time = models.DateTimeField(auto_now=True)


class ResourceLimit(models.Model):
    """
    Resource Limit for every pods/containers. Every application should have a
    resource limit. Default: cpu: m, memory: Mi
    """
    MEMORY_SIZE = (
        ('Ki', 'Ki'),
        ('Mi', 'Mi'),
        ('Gi', 'Gi')
    )

    name = models.CharField(max_length=32, default='')
    cpu = models.IntegerField()
    cpu_unit = models.CharField(max_length=4, default='m')
    memory = models.IntegerField()
    memory_unit = models.CharField(max_length=4, choices=MEMORY_SIZE,
        default='Mi')


class Application(models.Model):
    """
    Application represents the running image, which maybe an internal service or
    an external application.
    """
    STATUS_CHOICES = (
        ('creating', 'creating'),
        ('active', 'active'),
        ('down', 'down'),
        ('deleting', 'deleting'),
        ('deleted', 'deleted'),
        ('error', 'error'),
    )

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,
        default=True)
    image = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)
    resource_limit = models.ForeignKey(ResourceLimit, on_delete=models.CASCADE)

    name = models.CharField(max_length=32, default='')
    replicas = models.IntegerField()
    session_affinity = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
        default='creating')
    internal_ip = models.CharField(max_length=16, blank=True, null=True)
    external_ip = models.CharField(max_length=16, blank=True, null=True)
    create_time = models.DateTimeField(auto_now=True)

    is_autoscaler = models.BooleanField(default=False)


class AutoScaler(models.Model):
    """
    AutoScaler is to auto scale the application.
    """
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    min_replicas = models.IntegerField()
    max_replicas = models.IntegerField()
    cpu_target = models.IntegerField()


class Port(models.Model):
    """
    Ports for the application. The external_port represents the port of external
     service. The internal_port represents the port of internal service.
    """
    PROTOCOL_CHOICES = (
        ('TCP', 'TCP'),
        ('UDP', 'UDP'),
    )

    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=32, default='')
    protocol = models.CharField(max_length=3, choices=PROTOCOL_CHOICES,
        default='TCP')
    external_port = models.IntegerField(blank=True, null=True)
    internal_port = models.IntegerField()


class Environment(models.Model):
    """
    Environment variable for application.
    """
    app = models.ForeignKey(Application, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)
    value = models.CharField(max_length=32)


class Volume(models.Model):
    """
    Volume is for persistent storage. It can be mounted on to application and
    umounted.
    """
    CAPACITY_UNIT =(
        ('Ki', 'Ki'),
        ('Mi', 'Mi'),
        ('Gi', 'Gi')
    )

    STATUS_CHOICES = (
        ('creating', 'creating'),
        ('active', 'active'),
        ('deleting', 'deleting'),
        ('deleted', 'deleted'),
        ('error', 'error'),
    )

    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, null=True,
        default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    app = models.ForeignKey(Application, blank=True, null=True, on_delete=models.SET_NULL)
    mount_path = models.CharField(max_length=256, null=True, blank=True)
    name = models.CharField(max_length=32)
    desc = models.TextField(max_length=256, null=True)
    capacity = models.IntegerField()
    capacity_unit = models.CharField(max_length=4, choices=CAPACITY_UNIT,
        default='Mi')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
        default='creating')
    create_time = models.DateTimeField(auto_now=True)
