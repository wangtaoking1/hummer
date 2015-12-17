# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', null=True, blank=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(max_length=254, unique=True, db_index=True)),
                ('email', models.EmailField(verbose_name='email address', max_length=254)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('groups', models.ManyToManyField(verbose_name='groups', related_query_name='user', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group', blank=True, related_name='user_set')),
                ('user_permissions', models.ManyToManyField(verbose_name='user permissions', related_query_name='user', help_text='Specific permissions for this user.', to='auth.Permission', blank=True, related_name='user_set')),
            ],
        ),
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('desc', models.TextField(max_length=254, null=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('source', models.ForeignKey(to='backend.App', blank=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('desc', models.TextField(max_length=254, null=True)),
                ('version', models.CharField(max_length=32)),
                ('digest', models.CharField(default='', max_length=64, null=True, blank=True)),
                ('token', models.CharField(default='', max_length=64, null=True, blank=True)),
                ('is_public', models.BooleanField(verbose_name='public', default=False)),
                ('status', models.CharField(default='creating', max_length=16, choices=[('deleted', 'deleted'), ('deleting', 'deleting'), ('active', 'active'), ('creating', 'creating'), ('failed', 'failed')])),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(to='backend.App')),
            ],
        ),
    ]
