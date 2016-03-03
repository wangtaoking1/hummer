from django.conf.urls import include, url
from rest_framework import routers
from restapi.views import (UserViewSet, ProjectViewSet, ImageViewSet,
    ApplicationViewSet, PortViewSet, ResourceLimitViewSet, VolumeViewSet,
    is_authenticated, create_image, upload_volume)

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

urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'', include(router.urls)),

    # user
    url(r'users/(?P<pk>[0-9]+)/set_password/$', set_password,
        name='set-password'),
    url(r'auth/is_authenticated/$', is_authenticated, name='is_authenticated'),

    # create image
    url(r'projects/(?P<pid>[0-9]+)/create_image/$', create_image),

    # pod
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<pk>[0-9]+)/pods/$',
        pod_list, name='pod-list'),
    url(r'projects/(?P<pid>[0-9]+)/pods/(?P<pod>.+)/logs/$', logs_pod,
        name='logs-pod'),

    # port
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/ports/$',
        port_list, name='port-list'),
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/ports/\
(?P<pk>[0-9]+)/$', port_detail, name='port-detail'),

    # volume
    url(r'projects/(?P<pid>[0-9]+)/volumes/(?P<pk>[0-9]+)/download/$',
        volume_download, name='volume-download'),
    url(r'projects/(?P<pid>[0-9]+)/volumes/(?P<pk>[0-9]+)/upload/$',
        upload_volume, name='volume-upload'),
    url(r'projects/(?P<pid>[0-9]+)/volumes/(?P<pk>[0-9]+)/clear/$',
        clear_volume, name='volume-clear'),

    # public images
    url(r'publics/$', list_public_images, name='public-images'),
    url(r'publics/(?P<puid>[0-9]+)/$', get_public_image,
        name='get-public-image'),
    url(r'publics/(?P<puid>[0-9]+)/clone/$', add_public_image_to_project,
        name='clone-public-image'),

    # auth
    url(r'auth/', include('rest_framework.urls',
        namespace='rest_framework')),
]
