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
    url(r'^projects/(?P<pid>[0-9]+)/permission/$', views.user_permission,
        name='user-permission'),

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
    url(r'^projects/(?P<pid>[0-9]+)/create-application/$', views.create_application,
        name='create-application'),
    url(r'^projects/(?P<pid>[0-9]+)/pods/(?P<pod>.+)/logs/$',
        views.get_logs_of_pod, name='logs-pod'),

    # volume
    url(r'^projects/(?P<pid>[0-9]+)/volumes/$', views.list_volumes,
        name='list-volumes'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/$',
        views.show_volume_detail, name='show-volume-detail'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/delete_volume/$',
        views.delete_volume, name='delete-volume'),
    url(r'^projects/(?P<pid>[0-9]+)/create-volume/$', views.create_volume,
        name='create-volume'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/upload/$',
        views.upload_volume, name='upload-volume'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/download/$',
        views.download_volume, name='download-volume'),
    url(r'^projects/(?P<pid>[0-9]+)/volumes/(?P<vid>[0-9]+)/clear/$',
        views.clear_volume, name='clear-volume'),

    # public image
    url(r'^publics/$', views.list_publics, name='list-publics'),
    url(r'^publics/(?P<puid>[0-9]+)/$', views.show_public_detail,
        name='public-detail'),
    url(r'^publics/(?P<puid>[0-9]+)/clone/$', views.clone_public_image,
        name='public-clone'),

    # user management
    url(r'^user-management/$', views.user_management, name='user-management'),

    # resource module
    url(r'^resource-module/$', views.resource_module, name='resource-module'),
    url(r'^delete-module/(?P<mid>[0-9]+)/$', views.delete_resource_module,
        name='delete-module'),
    url(r'^create-module/$', views.create_resource_module,
        name='create-module'),

    # monitor
    url(r'^app-monitor/$', views.app_monitor, name='app-monitor'),
    url(r'^host-monitor/$', views.host_monitor, name='host-monitor'),
    url(r'^list-projects/$', views.list_projects, name='list-projects'),
    url(r'^list-apps/$', views.list_apps, name='list-apps'),
    url(r'^list-pods/$', views.list_pods, name='list-pods'),

    url(r'^test/$', views.test),
]
