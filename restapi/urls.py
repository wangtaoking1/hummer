from django.conf.urls import include, url
from rest_framework import routers
from restapi import views

router = routers.DefaultRouter()

urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'', include(router.urls)),
    url(r'users/$', views.UserList.as_view()),
    url(r'^users/(?P<pk>[a-z]+)/$', views.UserDetail.as_view()),

    url(r'auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]
