import requests
import logging

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.http import (require_http_methods, require_GET,
    require_POST)

from website.auth import login_required
from website.utils import (get_api_server_url)
from website.communicate import Communicator
from website.auth import is_authenticated
from website.forms import (LoginForm, RegistryForm)

logger = logging.getLogger("website")


def home(request):
    """
    Return the home page before login in.
    """
    if is_authenticated(request)[0]:
        return HttpResponseRedirect(reverse('index'))

    return render(request, 'website/home.html', locals(),
        RequestContext(request))


@require_POST
def login(request):
    """
    Login view.
    """
    form = LoginForm(data=request.POST)

    if form.is_valid():
        data = {
            'username': form.cleaned_data['username'],
            'password': form.cleaned_data['password']
        }
        client = Communicator()
        cookies = client.login(data)

        if 'sessionid' in cookies:
            response = HttpResponseRedirect(reverse('index'))
            response.set_cookie('sessionid', cookies['sessionid'])
            return response

        return HttpResponseRedirect(reverse('home'))
    return HttpResponseRedirect(reverse('home'))


def logout(request):
    """
    Logout view.
    """
    cookies = {'sessionid': request.COOKIES.get('sessionid', None)}
    client = Communicator(cookies=cookies)
    client.logout()
    return HttpResponseRedirect(reverse('home'))


@login_required()
def index(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }
    return render(request, 'website/dashboard.html', context)


@require_POST
def registry(request):
    """
    User registry view, should post username, password1, password2, email.
    """
    form = RegistryForm(request.POST)
    if form.is_valid() and form.password_varify():
        data = {
            'username': form.cleaned_data['username'],
            'password': form.cleaned_data['password1'],
            'email': form.cleaned_data['email'],
            'is_staff': False,
            'is_active': True
        }
        client = Communicator()
        cookies = client.registry(data)

        if 'sessionid' in cookies:
            response = HttpResponseRedirect(reverse('index'))
            response.set_cookie('sessionid', cookies['sessionid'])
            return response

    return HttpResponseRedirect(reverse('home'))
