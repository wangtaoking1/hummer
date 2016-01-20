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

    url(r'^projects/(?P<pid>[0-9]+)/introduction/$', views.project_home,
        name='introduce-project'),

    # image
    url(r'^projects/(?P<pid>[0-9]+)/images/$', views.list_images,
        name='list-images'),
    url(r'^projects/(?P<pid>[0-9]+)/images/(?P<iid>[0-9]+)/$',
        views.show_image_detail, name='show-image-detail'),

    # application
    url(r'^projects/(?P<pid>[0-9]+)/applications/$', views.list_applications,
        name='list-applications'),
    url(r'^projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/$',
        views.show_application_detail, name='show-application-detail'),

    # volume
    url(r'^projects/(?P<pid>[0-9]+)/volumes/$', views.list_volumes,
        name='list-volumes'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/$',
        views.show_volume_detail, name='show-volume-detail'),

    # public image
    url(r'^projects/(?P<pid>[0-9]+)/publics/$', views.list_publics,
        name='list-publics'),


]
