from django.conf.urls import include, url
from rest_framework import routers
from restapi.views import (UserViewSet, ProjectViewSet, ImageViewSet,
    ApplicationViewSet, PortViewSet, ResourceLimitViewSet, VolumeViewSet,
    is_authenticated, create_image, upload_volume, list_hosts,
    AutoScalerViewSet, EnvironmentViewSet, registry)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet, base_name='project')
router.register(r'projects/(?P<pid>[0-9]+)/images', ImageViewSet,
    base_name='image')
router.register(r'projects/(?P<pid>[0-9]+)/applications', ApplicationViewSet,
    base_name='application')
router.register(r'projects/(?P<pid>[0-9]+)/volumes', VolumeViewSet,
    base_name='volume')
router.register(r'resourcelimits', ResourceLimitViewSet,
    base_name='resourcelimit')

set_password = UserViewSet.as_view({
    'post': 'set_password'
})

port_list = PortViewSet.as_view({
    'get': 'list'
})
port_detail = PortViewSet.as_view({
    'get': 'retrieve'
})

volume_download = VolumeViewSet.as_view({
    'get': 'download'
})

clear_volume = VolumeViewSet.as_view({
    'get': 'clear_volume'
})

get_volume_username = VolumeViewSet.as_view({
    'get': 'get_volume_username'
})

pod_list = ApplicationViewSet.as_view({
    'get': 'pod_lists'
})

logs_pod = ApplicationViewSet.as_view({
    'get': 'logs_pod'
})

list_public_images = ImageViewSet.as_view({
    'get': 'list_public_images'
})

get_public_image = ImageViewSet.as_view({
    'get': 'get_public_image'
})

add_public_image_to_project = ImageViewSet.as_view({
    'post': 'add_public_image_to_project'
})

get_image_username = ImageViewSet.as_view({
    'get': 'get_image_username'
})

add_users = ProjectViewSet.as_view({
    'post': 'add_users'
})

remove_users = ProjectViewSet.as_view({
    'post': 'remove_users'
})

list_members = ProjectViewSet.as_view({
    'get': 'list_members'
})

list_projects = ProjectViewSet.as_view({
    'get': 'list_projects'
})

get_application_username = ApplicationViewSet.as_view({
    'get': 'get_application_username'
})

list_applications = ApplicationViewSet.as_view({
    'get': 'list_applications'
})

list_pods = ApplicationViewSet.as_view({
    'get': 'list_pods'
})

list_autoscalers = AutoScalerViewSet.as_view({
    'get': 'list'
})
get_autoscaler_detail = AutoScalerViewSet.as_view({
    'get': 'retrieve'
})

list_environments = EnvironmentViewSet.as_view({
    'get': 'list'
})
get_environment_detail = EnvironmentViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'', include(router.urls)),

    # user
    url(r'registry/$', registry, name='registry'),
    url(r'users/(?P<pk>[0-9]+)/set_password/$', set_password,
        name='set-password'),
    url(r'auth/is_authenticated/$', is_authenticated, name='is_authenticated'),

    # create image
    url(r'projects/(?P<pid>[0-9]+)/create_image/$', create_image),
    url(r'projects/(?P<pid>[0-9]+)/images/(?P<pk>[0-9]+)/username/$',
        get_image_username, name='image-username'),

    # pod
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<pk>[0-9]+)/pods/$',
        pod_list, name='pod-list'),
    url(r'projects/(?P<pid>[0-9]+)/pods/(?P<pod>.+)/logs/$', logs_pod,
        name='logs-pod'),

    # port
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/ports/$',
        port_list, name='port-list'),
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/ports/(?P<pk>[0-9]+)/$', port_detail, name='port-detail'),

    # environment
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/envs/$',
        list_environments, name='envs-list'),
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/envs/(?P<pk>[0-9]+)/$', get_environment_detail, name='env-detail'),

    # autoscaler
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/scalers/$',
        list_autoscalers, name='list-autoscalers'),
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/scalers/(?P<pk>[0-9]+)/$', get_autoscaler_detail, name='autoscaler-detail'),

    # volume
    url(r'projects/(?P<pid>[0-9]+)/volumes/(?P<pk>[0-9]+)/download/$',
        volume_download, name='volume-download'),
    url(r'projects/(?P<pid>[0-9]+)/volumes/(?P<pk>[0-9]+)/upload/$',
        upload_volume, name='volume-upload'),
    url(r'projects/(?P<pid>[0-9]+)/volumes/(?P<pk>[0-9]+)/clear/$',
        clear_volume, name='volume-clear'),
    url(r'projects/(?P<pid>[0-9]+)/volumes/(?P<pk>[0-9]+)/username/$',
        get_volume_username, name='volume-username'),

    # public images
    url(r'publics/$', list_public_images, name='public-images'),
    url(r'publics/(?P<puid>[0-9]+)/$', get_public_image,
        name='get-public-image'),
    url(r'publics/(?P<puid>[0-9]+)/clone/$', add_public_image_to_project,
        name='clone-public-image'),

    # hosts
    url(r'hosts/$', list_hosts, name='list-hosts'),

    # projects
    url(r'list-projects/$', list_projects, name='list-projects'),
    url(r'projects/(?P<pk>[0-9]+)/add_users/$', add_users, name='add-users'),
    url(r'projects/(?P<pk>[0-9]+)/remove_users/$', remove_users,
        name='remove-users'),
    url(r'projects/(?P<pk>[0-9]+)/members/$', list_members, name='members'),

    # applications
    url(r'list-apps/$', list_applications, name='list-apps'),
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<pk>[0-9]+)/username/$',
        get_application_username, name='application-username'),

    # pods
    url(r'list-pods/$', list_pods, name='list-pods'),

    # auth
    url(r'auth/', include('rest_framework.urls',
        namespace='rest_framework')),
]
