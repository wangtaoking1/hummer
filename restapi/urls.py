from django.conf.urls import include, url
from rest_framework import routers
from restapi.views import (UserViewSet, ProjectViewSet, ImageViewSet,
    ApplicationViewSet, PortViewSet, ResourceLimitViewSet, VolumeViewSet)

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

port_list = PortViewSet.as_view({
    'get': 'list'
})
port_detail = PortViewSet.as_view({
    'get': 'retrieve'
})

urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'', include(router.urls)),
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/ports/$',
        port_list, name='port-list'),
    url(r'projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/ports/(?P<pk>[0-9]+)/$',
        port_detail, name='port-detail'),

    url(r'auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
