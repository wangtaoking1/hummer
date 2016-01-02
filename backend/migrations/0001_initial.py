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
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', blank=True, null=True)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(db_index=True, unique=True, max_length=254)),
                ('email', models.EmailField(verbose_name='email address', max_length=254)),
                ('is_staff', models.BooleanField(verbose_name='staff status', default=False)),
                ('is_active', models.BooleanField(verbose_name='active', default=True)),
                ('groups', models.ManyToManyField(related_name='user_set', verbose_name='groups', blank=True, related_query_name='user', to='auth.Group', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', verbose_name='user permissions', blank=True, related_query_name='user', to='auth.Permission', help_text='Specific permissions for this user.')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, default='')),
                ('replicas', models.IntegerField()),
                ('session_affinity', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=10, default='creating', choices=[('creating', 'creating'), ('active', 'active'), ('down', 'down'), ('deleting', 'deleting'), ('deleted', 'deleted'), ('error', 'error')])),
                ('internal_ip', models.CharField(blank=True, null=True, max_length=16)),
                ('external_ip', models.CharField(blank=True, null=True, max_length=16)),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, default='')),
                ('desc', models.TextField(null=True, max_length=254)),
                ('version', models.CharField(max_length=32)),
                ('digest', models.CharField(blank=True, null=True, max_length=64, default='')),
                ('token', models.CharField(blank=True, null=True, max_length=64, default='')),
                ('is_public', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=16, default='creating', choices=[('deleted', 'deleted'), ('deleting', 'deleting'), ('active', 'active'), ('creating', 'creating'), ('failed', 'failed')])),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64, default='')),
                ('protocol', models.CharField(max_length=3, default='TCP', choices=[('TCP', 'TCP'), ('UDP', 'UDP')])),
                ('external_port', models.IntegerField(blank=True, null=True)),
                ('internal_port', models.IntegerField()),
                ('app', models.ForeignKey(to='backend.Application')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=128, default='')),
                ('desc', models.TextField(null=True, max_length=254)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceLimit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=32, default='')),
                ('cpu', models.IntegerField()),
                ('cpu_unit', models.CharField(max_length=4, default='m')),
                ('memory', models.IntegerField()),
                ('memory_unit', models.CharField(max_length=4, default='Mi', choices=[('Ki', 'Ki'), ('Mi', 'Mi'), ('Gi', 'Gi')])),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='project',
            field=models.ForeignKey(to='backend.Project'),
        ),
        migrations.AddField(
            model_name='application',
            name='image',
            field=models.ForeignKey(to='backend.Image'),
        ),
        migrations.AddField(
            model_name='application',
            name='resource_limit',
            field=models.ForeignKey(to='backend.ResourceLimit'),
        ),
    ]
