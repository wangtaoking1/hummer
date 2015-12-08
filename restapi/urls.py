from django.conf.urls import include, url
from rest_framework import routers
from restapi.views import UserViewSet, AppViewSet, ImageViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'apps', AppViewSet, base_name="app")
router.register(r'images', ImageViewSet, base_name='image')

urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'', include(router.urls)),

    url(r'auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
