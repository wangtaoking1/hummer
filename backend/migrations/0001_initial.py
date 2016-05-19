# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='MyUser',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(help_text='Designates that this user has all permissions without explicitly assigning them.', default=False, verbose_name='superuser status')),
                ('username', models.CharField(max_length=32, db_index=True, unique=True)),
                ('email', models.EmailField(max_length=256, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('groups', models.ManyToManyField(blank=True, related_query_name='user', related_name='user_set', verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', to='auth.Group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_query_name='user', related_name='user_set', verbose_name='user permissions', help_text='Specific permissions for this user.', to='auth.Permission')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=32, default='')),
                ('replicas', models.IntegerField()),
                ('session_affinity', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=10, choices=[('creating', 'creating'), ('active', 'active'), ('down', 'down'), ('deleting', 'deleting'), ('deleted', 'deleted'), ('error', 'error')], default='creating')),
                ('internal_ip', models.CharField(blank=True, null=True, max_length=16)),
                ('external_ip', models.CharField(blank=True, null=True, max_length=16)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('is_autoscaler', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='AutoScaler',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('min_replicas', models.IntegerField()),
                ('max_replicas', models.IntegerField()),
                ('cpu_target', models.IntegerField()),
                ('app', models.ForeignKey(to='backend.Application')),
            ],
        ),
        migrations.CreateModel(
            name='Environment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=32)),
                ('app', models.ForeignKey(to='backend.Application')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=32, default='')),
                ('desc', models.TextField(max_length=256, null=True)),
                ('version', models.CharField(max_length=32)),
                ('digest', models.CharField(default='', blank=True, null=True, max_length=64)),
                ('token', models.CharField(default='', blank=True, null=True, max_length=64)),
                ('is_public', models.BooleanField(default=False)),
                ('status', models.CharField(max_length=16, choices=[('deleted', 'deleted'), ('deleting', 'deleting'), ('active', 'active'), ('creating', 'creating'), ('failed', 'failed')], default='creating')),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=32, default='')),
                ('protocol', models.CharField(max_length=3, choices=[('TCP', 'TCP'), ('UDP', 'UDP')], default='TCP')),
                ('external_port', models.IntegerField(blank=True, null=True)),
                ('internal_port', models.IntegerField()),
                ('app', models.ForeignKey(to='backend.Application')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=32, default='')),
                ('desc', models.TextField(max_length=256, null=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceLimit',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=32, default='')),
                ('cpu', models.IntegerField()),
                ('cpu_unit', models.CharField(max_length=4, default='m')),
                ('memory', models.IntegerField()),
                ('memory_unit', models.CharField(max_length=4, choices=[('Ki', 'Ki'), ('Mi', 'Mi'), ('Gi', 'Gi')], default='Mi')),
            ],
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('mount_path', models.CharField(blank=True, null=True, max_length=256)),
                ('name', models.CharField(max_length=32)),
                ('desc', models.TextField(max_length=256, null=True)),
                ('capacity', models.IntegerField()),
                ('capacity_unit', models.CharField(max_length=4, choices=[('Ki', 'Ki'), ('Mi', 'Mi'), ('Gi', 'Gi')], default='Mi')),
                ('status', models.CharField(max_length=10, choices=[('creating', 'creating'), ('active', 'active'), ('deleting', 'deleting'), ('deleted', 'deleted'), ('error', 'error')], default='creating')),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='backend.Application', null=True)),
                ('project', models.ForeignKey(to='backend.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, default=True)),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='project',
            field=models.ForeignKey(to='backend.Project', null=True, default=True),
        ),
        migrations.AddField(
            model_name='image',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, default=True),
        ),
        migrations.AddField(
            model_name='application',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='backend.Image', null=True),
        ),
        migrations.AddField(
            model_name='application',
            name='resource_limit',
            field=models.ForeignKey(to='backend.ResourceLimit'),
        ),
        migrations.AddField(
            model_name='application',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, default=True),
        ),
    ]
