from django.conf.urls import include, url
from rest_framework import routers
from restapi.views import UserViewSet

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'', include(router.urls)),

    url(r'auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
