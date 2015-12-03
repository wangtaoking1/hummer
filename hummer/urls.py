from django.conf.urls import include, url


urlpatterns = [
    # Examples:
    # url(r'^$', 'hummer.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^api/', include('restapi.urls')),
]
