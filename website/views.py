import requests
import logging
import os
import time

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.http import (require_http_methods, require_GET,
    require_POST)
from django.views.decorators.csrf import csrf_exempt

from website.auth import login_required
from website.utils import (get_api_server_url, save_buildfile_to_disk,
    get_filename_of_buildfile)
from website.communicate import Communicator
from website.auth import is_authenticated
from website.forms import (LoginForm, RegistryForm, ProjectForm, SourceForm,
    ImageForm, SnapshotForm)

logger = logging.getLogger("website")


def index(request):
    """
    Return the dashboard page before login in.
    """
    if is_authenticated(request)[0]:
        return HttpResponseRedirect(reverse('dashboard'))

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
            response = HttpResponseRedirect(reverse('dashboard'))
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
            response = HttpResponseRedirect(reverse('dashboard'))
            response.set_cookie('sessionid', cookies['sessionid'])
            return response

        return HttpResponseRedirect(reverse('index'))
    return HttpResponseRedirect(reverse('index'))


def logout(request):
    """
    Logout view.
    """
    client = Communicator(cookies=request.COOKIES)
    client.logout()
    return HttpResponseRedirect(reverse('index'))


@login_required()
def dashboard(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }

    client = Communicator(cookies=request.COOKIES)

    # Get project lists
    projects = client.project_lists()
    context['projects'] = projects

    return render(request, 'website/dashboard.html', context,
        RequestContext(request))


@login_required()
@csrf_exempt
@require_POST
def create_project(request, *args, **kwargs):
    form = ProjectForm(request.POST)
    if not form.is_valid():
        return HttpResponseRedirect(reverse('dashboard'))

    client = Communicator(cookies=request.COOKIES)
    data = {
        'name': form.cleaned_data['name'],
        'desc': form.cleaned_data['desc'],
        'csrfmiddlewaretoken': request.POST['csrfmiddlewaretoken']
    }

    ok = client.create_project(data)
    logger.debug(ok)
    return HttpResponseRedirect(reverse('dashboard'))


@login_required()
def delete_project(request, *args, **kwargs):
    project_id = kwargs['pid']

    client = Communicator(cookies=request.COOKIES)
    ok = client.delete_project(project_id)
    if ok:
        return HttpResponseRedirect(reverse('dashboard'))
    return HttpResponseRedirect(reverse('dashboard'))


@login_required()
def project_intro(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }
    project_id = kwargs['pid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)

    return render(request, 'website/project_intro.html', context,
        RequestContext(request))


@login_required()
def list_images(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }

    project_id = kwargs.get('pid')
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['images'] = client.image_lists(project_id=project_id)

    return render(request, 'website/images.html', context,
        RequestContext(request))


@login_required()
def delete_image(request, *args, **kwargs):
    project_id = kwargs['pid']
    image_id = kwargs['iid']

    client = Communicator(cookies=request.COOKIES)
    ok = client.delete_image(project_id=project_id, image_id=image_id)
    if ok:
        return HttpResponseRedirect(reverse('list-images',
            kwargs={'pid': project_id}))
    return HttpResponseRedirect(reverse('list-images',
        kwargs={'pid': project_id}))


@login_required()
@csrf_exempt
@require_POST
def upload_build_file(request, *args, **kwargs):
    project_id = kwargs['pid']

    save_buildfile_to_disk(request.FILES['file'], project_id)
    return JsonResponse({})


@login_required()
@csrf_exempt
@require_POST
def create_image(request, *args, **kwargs):
    project_id = kwargs['pid']

    build_type = request.POST.get('build_type', '0')
    if build_type == '0':
        form = SourceForm(request.POST)
    elif build_type == '1':
        form = ImageForm(request.POST)
    elif build_type == '2':
        form= SnapshotForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"error": "data invalid"})

    buildfile = get_filename_of_buildfile(project_id)
    if form.cleaned_data['image_type'] == '0':
        is_public = 'false'
    else:
        is_public = 'true'
    data = {
        'name': form.cleaned_data['name'],
        'version': form.cleaned_data['version'],
        'desc': form.cleaned_data['desc'],
        'is_public': is_public,
        'is_image': form.cleaned_data['build_type'],
    }

    build_type = form.cleaned_data['build_type']
    if build_type == '0':
        data['dockerfile'] = form.cleaned_data['dockerfile']
    elif build_type == '1':
        data['old_image_name'] = form.cleaned_data['old_name']
        data['old_image_version'] = form.cleaned_data['old_version']

    client = Communicator(cookies=request.COOKIES)
    ok = client.create_image(project_id, data, buildfile)
    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


@login_required()
def list_applications(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }
    project_id = kwargs['pid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['applications'] = client.application_lists(project_id=project_id)

    return render(request, 'website/applications.html', context,
        RequestContext(request))


@login_required()
def delete_application(request, *args, **kwargs):
    project_id = kwargs['pid']
    application_id = kwargs['aid']

    client = Communicator(cookies=request.COOKIES)
    ok = client.delete_application(project_id=project_id,
        application_id=application_id)
    if ok:
        return HttpResponseRedirect(reverse('list-applications',
            kwargs={'pid': project_id}))
    return HttpResponseRedirect(reverse('list-applications',
        kwargs={'pid': project_id}))


@login_required()
def list_volumes(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }
    project_id = kwargs['pid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['volumes'] = client.volume_lists(project_id=project_id)

    return render(request, 'website/volumes.html', context,
        RequestContext(request))


@login_required()
def delete_volume(request, *args, **kwargs):
    project_id = kwargs['pid']
    volume_id = kwargs['vid']

    client = Communicator(cookies=request.COOKIES)
    ok = client.delete_volume(project_id=project_id,
        volume_id=volume_id)
    if ok:
        return HttpResponseRedirect(reverse('list-volumes',
            kwargs={'pid': project_id}))
    return HttpResponseRedirect(reverse('list-volumes',
        kwargs={'pid': project_id}))


@login_required()
def list_publics(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }
    return render(request, 'website/public_images.html', context,
        RequestContext(request))


@login_required()
def show_image_detail(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }
    project_id = kwargs['pid']
    image_id = kwargs['iid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['image'] = client.get_image(project_id=project_id,
        image_id=image_id)

    return render(request, 'website/image_detail.html', context,
        RequestContext(request))


@login_required()
def show_application_detail(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }
    project_id = kwargs['pid']
    application_id = kwargs['aid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['application'] = client.get_application(project_id=project_id,
        application_id=application_id)

    return render(request, 'website/application_detail.html', context,
        RequestContext(request))


@login_required()
def show_volume_detail(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username')
    }

    project_id = kwargs['pid']
    volume_id = kwargs['vid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['volume'] = client.get_volume(project_id=project_id,
        volume_id=volume_id)

    return render(request, 'website/volume_detail.html', context,
        RequestContext(request))


@login_required()
@csrf_exempt
@require_POST
def test(request, *args, **kwargs):
    print(request.POST)
    if not request.FILES.get('file'):
        return JsonResponse({"error": "no file"})
    return JsonResponse({"success": "success"})
