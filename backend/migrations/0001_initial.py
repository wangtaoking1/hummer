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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(unique=True, max_length=254, db_index=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('groups', models.ManyToManyField(related_name='user_set', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_query_name='user', to='auth.Group', verbose_name='groups', blank=True)),
                ('user_permissions', models.ManyToManyField(related_name='user_set', help_text='Specific permissions for this user.', related_query_name='user', to='auth.Permission', verbose_name='user permissions', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('desc', models.TextField(max_length=254, null=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('source', models.ForeignKey(null=True, to='backend.App', blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(max_length=128)),
                ('desc', models.TextField(max_length=254, null=True)),
                ('version', models.CharField(max_length=32)),
                ('token', models.CharField(max_length=64)),
                ('is_public', models.BooleanField(default=False, verbose_name='public')),
                ('status', models.CharField(default='creating', max_length=16, choices=[('deleted', 'deleted'), ('deleting', 'deleting'), ('active', 'active'), ('creating', 'creating')])),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(to='backend.App')),
            ],
        ),
    ]
