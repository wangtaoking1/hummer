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
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^create_project/$', views.create_project, name='create-project'),
    url(r'^projects/(?P<pid>[0-9]+)/delete_project/$', views.delete_project,
        name='delete-project'),

    # project introduction
    url(r'^projects/(?P<pid>[0-9]+)/introduction/$', views.project_intro,
        name='introduce-project'),

    # image
    url(r'^projects/(?P<pid>[0-9]+)/images/$', views.list_images,
        name='list-images'),
    url(r'^projects/(?P<pid>[0-9]+)/uploadfile/$', views.upload_build_file,
        name='upload-file'),
    url(r'^projects/(?P<pid>[0-9]+)/images/(?P<iid>[0-9]+)/$',
        views.show_image_detail, name='show-image-detail'),
    url(r'^projects/(?P<pid>[0-9]+)/images/(?P<iid>[0-9]+)/delete_image/$',
        views.delete_image, name='delete-image'),
    url(r'^projects/(?P<pid>[0-9]+)/create-image/$', views.create_image,
        name='create-image'),

    # application
    url(r'^projects/(?P<pid>[0-9]+)/applications/$', views.list_applications,
        name='list-applications'),
    url(r'^projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/$',
        views.show_application_detail, name='show-application-detail'),
    url(r'^projects/(?P<pid>[0-9]+)/applications/(?P<aid>[0-9]+)/delete_application/$',
        views.delete_application, name='delete-application'),

    # volume
    url(r'^projects/(?P<pid>[0-9]+)/volumes/$', views.list_volumes,
        name='list-volumes'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/$',
        views.show_volume_detail, name='show-volume-detail'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/delete_volume/$',
        views.delete_volume, name='delete-volume'),

    # public image
    url(r'^projects/(?P<pid>[0-9]+)/publics/$', views.list_publics,
        name='list-publics'),


    url(r'^test/$', views.test),
]
