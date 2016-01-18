from django.conf.urls import include, url
from website import views


app_name = 'website'
urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^registry/$', views.registry, name='registry'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^home/$', views.home, name='home'),
    url(r'^create_project/$', views.create_project, name='create-project'),
    url(r'^delete_project/$', views.delete_project, name='delete-project'),
]
