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
from website.forms import (LoginForm, RegistryForm, ProjectForm)

logger = logging.getLogger("website")


def index(request):
    """
    Return the home page before login in.
    """
    if is_authenticated(request)[0]:
        return HttpResponseRedirect(reverse('home'))

    return render(request, 'website/index.html', locals(),
        RequestContext(request))


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
            response = HttpResponseRedirect(reverse('home'))
            response.set_cookie('sessionid', cookies['sessionid'])
            return response

    return HttpResponseRedirect(reverse('index'))


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
            response = HttpResponseRedirect(reverse('home'))
            response.set_cookie('sessionid', cookies['sessionid'])
            return response

        return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(reverse('index'))


def logout(request):
    """
    Logout view.
    """
    cookies = {'sessionid': request.COOKIES.get('sessionid', None)}
    client = Communicator(cookies=cookies)
    client.logout()
    return HttpResponseRedirect(reverse('index'))


@login_required()
def home(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }

    cookies = {'sessionid': request.COOKIES.get('sessionid', None)}
    client = Communicator(cookies=cookies)

    # Get project lists
    projects = client.project_lists()
    context['projects'] = projects

    return render(request, 'website/home.html', context,
        RequestContext(request))


@login_required()
@require_POST
def create_project(request, *args, **kwargs):
    form = ProjectForm(request.POST)
    if not form.is_valid():
        return HttpResponseRedirect(reverse('home'))

    cookies = {
        'sessionid': request.COOKIES.get('sessionid', None),
        'csrftoken': request.COOKIES.get('csrftoken', None)
    }
    client = Communicator(cookies=cookies)
    data = {
        'name': form.cleaned_data['name'],
        'desc': form.cleaned_data['desc'],
        'csrfmiddlewaretoken': request.POST['csrfmiddlewaretoken']
    }

    ok = client.create_project(data)
    logger.debug(ok)
    return HttpResponseRedirect(reverse('home'))


@login_required()
@require_POST
def delete_project(request, *args, **kwargs):
    logger.debug("13231231323123")
    return HttpResponseRedirect(reverse('home'))
