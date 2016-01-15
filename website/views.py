import requests
import logging

from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from website.utils import (get_api_server_url)
from website.communicate import Communicator
from website.auth import is_authenticated

logger = logging.getLogger("website")


def home(request):
    """
    Return the home page before login in.
    """
    if is_authenticated(request):
        return HttpResponseRedirect(reverse('index'))

    return render(request, 'website/homepage.html', locals(),
        RequestContext(request))


def login(request):
    """
    Login view.
    """
    form = AuthenticationForm(request, data=request.POST)

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
def index(request):
    context = {
        'user': request.user
    }
    return render(request, 'website/dashboard.html', context)
