from django.conf.urls import include, url
from rest_framework import routers
from restapi.views import (UserViewSet, ProjectViewSet, ImageViewSet,
    ApplicationViewSet)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'projects', ProjectViewSet, base_name='project')
router.register(r'projects/(?P<pid>[0-9]+)/images', ImageViewSet,
    base_name='image')
router.register(r'projects/(?P<pid>[0-9]+)/applications', ApplicationViewSet,
    base_name='application')

urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'', include(router.urls)),
    url(r'auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
