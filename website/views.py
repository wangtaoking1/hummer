import requests

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from website.utils import (get_api_server_url)


def home(request):
    """
    Return the home page before login in.
    """
    if request.user and request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))

    return render(request, 'website/homepage.html', locals(),
        RequestContext(request))


def login(request):
    """
    Login view.
    """
    form = AuthenticationForm(request, data=request.POST)

    if form.is_valid():
        username = request.POST['username']
        password = request.POST['password']
        csrf_token = request.COOKIES['csrftoken']

        url = get_api_server_url('/api/auth/login/')
        client = requests.session()
        client.cookies['csrftoken'] = csrf_token
        data = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': csrf_token
        }
        client.post(url, data)

        if 'sessionid' in client.cookies:
            response = HttpResponseRedirect(reverse('index'))
            response.set_cookie('sessionid', client.cookies['sessionid'])
            return response

        return HttpResponseRedirect(reverse('home'))
    return HttpResponseRedirect(reverse('home'))


def logout(request):
    """
    Logout view.
    """
    url = get_api_server_url('/api/auth/logout/')
    client = requests.session()
    client.cookies['sessionid'] = request.COOKIES['sessionid']
    client.get(url)
    return HttpResponseRedirect(reverse('home'))


@login_required()
def index(request):
    context = {
        'user': request.user
    }
    return render(request, 'website/dashboard.html', context)
