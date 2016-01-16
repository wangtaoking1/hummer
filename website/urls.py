from django.conf.urls import include, url
from website import views


app_name = 'website'
urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login, name='login'),
    url(r'^registry/$', views.registry, name='registry'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^index/$', views.index, name='index'),
]
