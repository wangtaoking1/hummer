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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, verbose_name='last login', null=True)),
                ('is_superuser', models.BooleanField(default=False, verbose_name='superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('username', models.CharField(unique=True, max_length=254, db_index=True)),
                ('email', models.EmailField(max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, verbose_name='active')),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', verbose_name='groups', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', verbose_name='user permissions', to='auth.Permission', blank=True, help_text='Specific permissions for this user.')),
            ],
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=128)),
                ('replicas', models.IntegerField()),
                ('session_affinity', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('creating', 'creating'), ('active', 'active'), ('down', 'down'), ('deleting', 'deleting'), ('deleted', 'deleted'), ('error', 'error')], default='creating', max_length=10)),
                ('internal_ip', models.CharField(blank=True, max_length=16, null=True)),
                ('external_ip', models.CharField(blank=True, max_length=16, null=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=128)),
                ('desc', models.TextField(max_length=254, null=True)),
                ('version', models.CharField(max_length=32)),
                ('digest', models.CharField(default='', blank=True, max_length=64, null=True)),
                ('token', models.CharField(default='', blank=True, max_length=64, null=True)),
                ('is_public', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('deleted', 'deleted'), ('deleting', 'deleting'), ('active', 'active'), ('creating', 'creating'), ('failed', 'failed')], default='creating', max_length=16)),
                ('create_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Port',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=64)),
                ('protocol', models.CharField(choices=[('TCP', 'TCP'), ('UDP', 'UDP')], default='TCP', max_length=3)),
                ('external_port', models.IntegerField(blank=True, null=True)),
                ('internal_port', models.IntegerField()),
                ('app', models.ForeignKey(to='backend.Application')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=128)),
                ('desc', models.TextField(max_length=254, null=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ResourceLimit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=32)),
                ('cpu', models.IntegerField()),
                ('cpu_unit', models.CharField(default='m', max_length=4)),
                ('memory', models.IntegerField()),
                ('memory_unit', models.CharField(choices=[('Ki', 'Ki'), ('Mi', 'Mi'), ('Gi', 'Gi')], default='Mi', max_length=4)),
            ],
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mount_path', models.CharField(blank=True, max_length=256, null=True)),
                ('name', models.CharField(max_length=64)),
                ('desc', models.TextField(max_length=254, null=True)),
                ('capacity', models.IntegerField()),
                ('capacity_unit', models.CharField(choices=[('Ki', 'Ki'), ('Mi', 'Mi'), ('Gi', 'Gi')], default='Mi', max_length=4)),
                ('status', models.CharField(choices=[('creating', 'creating'), ('active', 'active'), ('deleting', 'deleting'), ('deleted', 'deleted'), ('error', 'error')], default='creating', max_length=10)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('app', models.ForeignKey(blank=True, to='backend.Application', null=True)),
                ('project', models.ForeignKey(to='backend.Project')),
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
