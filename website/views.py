import requests
import logging
import os
import time
import json

from django.conf import settings
from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseRedirect, JsonResponse,
    StreamingHttpResponse)
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.decorators.http import (require_http_methods, require_GET,
    require_POST)
from django.views.decorators.csrf import csrf_exempt

from website.auth import login_required
from website.utils import (get_api_server_url, save_buildfile_to_disk,
    get_filename_of_buildfile, get_envs, get_ports, get_volumes,
    save_volume_data_to_disk, get_filename_of_volume_data,
    get_url_of_monitor_iframe, get_url_of_host_monitor,
    remove_buildfile_from_disk)
from website.communicate import Communicator
from website.auth import is_authenticated
from website.forms import (LoginForm, RegistryForm, ProjectForm, SourceForm,
    ImageForm, SnapshotForm, ApplicationForm, VolumeForm, PublicForm,
    ResourceModuleForm)

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
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
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
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }
    project_id = kwargs['pid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)

    return render(request, 'website/project_intro.html', context,
        RequestContext(request))


@login_required()
def user_permission(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }

    project_id = kwargs['pid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)

    all_users = client.list_users()
    selected_users = client.list_members(project_id=project_id)

    left_users = []
    for user in all_users:
        user_id = user['id']
        flag = False
        for item in selected_users:
            if item['id'] == user_id:
                flag = True
                break
        if not flag:
            left_users.append(user)
    context['left_users'] = left_users
    context['selected_users'] = selected_users

    return render(request, 'website/user_permission.html', context,
        RequestContext(request))


@login_required()
def list_images(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
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

    logger.debug(data)

    client = Communicator(cookies=request.COOKIES)
    ok = client.create_image(project_id, data, buildfile)

    remove_buildfile_from_disk(buildfile)

    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


@login_required()
def list_applications(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }
    project_id = kwargs['pid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['applications'] = client.application_lists(project_id=project_id)

    return render(request, 'website/applications.html', context,
        RequestContext(request))


@login_required()
@csrf_exempt
@require_POST
def create_application(request, *args, **kwargs):
    project_id = kwargs['pid']

    #TODO: Check validation

    form = ApplicationForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": "data invalid"})

    service_type = (False if form.cleaned_data['service_type'] == 'false'
        else True)
    session_affinity = (False if form.cleaned_data['session_affinity'] ==
        'false' else True)
    autoscaler = (False if form.cleaned_data['autoscaler'] == 'false'
        else True )
    # logger.debug(service_type)
    # logger.debug(session_affinity)

    data = {
        'image': form.cleaned_data['image'],
        'name': form.cleaned_data['name'],
        'replicas': form.cleaned_data['replicas'],
        'resource_limit': form.cleaned_data['resource_limit'],
        'is_public': service_type,
        'session_affinity': session_affinity,
        'is_autoscaler': autoscaler
    }

    # envs
    envs = get_envs(form.cleaned_data['env_number'], request.POST)
    if envs:
        data['envs'] = envs

    # ports
    ports = get_ports(form.cleaned_data['port_number'], request.POST)
    if ports:
        data['ports'] = ports

    # volumes
    volumes = get_volumes(form.cleaned_data['volume_number'], request.POST)
    if volumes:
        data['volumes'] = volumes

    # autoscale
    if autoscaler:
        data['min_replicas'] = request.POST.get('min_replicas', -1)
        data['max_replicas'] = request.POST.get('max_replicas', -1)
        data['cpu_target'] = request.POST.get('cpu_target', -1)

    logger.debug(data)

    # data = {
    #     'image': 1,
    #     'session_affinity': False,
    #     'name': 'test',
    #     'resource_limit': 1,
    #     'replicas': 1,
    #     'ports': [
    #         {'port': 80, 'protocol': 'TCP', 'name': 'http'}
    #     ],
    #     'is_public': True,
    #     'volumes': [
    #         {'volume': 2, 'mount_path': '/var/www/html'}
    #     ]
    # }

    client = Communicator(cookies=request.COOKIES)
    ok = client.create_application(project_id, data)
    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


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
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }
    project_id = kwargs['pid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['volumes'] = client.volume_lists(project_id=project_id)

    return render(request, 'website/volumes.html', context,
        RequestContext(request))


@login_required()
@csrf_exempt
@require_POST
def create_volume(request, *args, **kwargs):
    project_id = kwargs['pid']

    #TODO: Check validation

    form = VolumeForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": "data invalid"})

    data = {
        'project': int(project_id),
        'name': form.cleaned_data['name'],
        'desc': form.cleaned_data['desc'],
        'capacity': int(form.cleaned_data['capacity']),
        'capacity_unit': form.cleaned_data['capacity_unit']
    }

    logger.debug(data)

    client = Communicator(cookies=request.COOKIES)
    ok = client.create_volume(project_id, data)
    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


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
@csrf_exempt
@require_POST
def upload_volume(request, *args, **kwargs):
    """
    Upload data into volume.
    """
    pid = kwargs['pid']
    vid = kwargs['vid']

    client = Communicator(cookies=request.COOKIES)
    ok = client.upload_to_volume(pid, vid, request.FILES['file'])

    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


@login_required()
def download_volume(request, *args, **kwargs):
    """
    Download data from volume.
    """
    pid = kwargs['pid']
    vid = kwargs['vid']

    client = Communicator(cookies=request.COOKIES)
    volume = client.get_volume(project_id=pid, volume_id=vid)
    res = client.download_from_volume(pid, vid)

    response = StreamingHttpResponse(res.iter_content(chunk_size=512))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(
        volume['name'] + ".tar")
    return response


@login_required()
def clear_volume(request, *args, **kwargs):
    """
    Clear data of volume.
    """
    pid = kwargs['pid']
    vid = kwargs['vid']

    client = Communicator(cookies=request.COOKIES)
    ok = client.clear_volume(pid, vid)
    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


@login_required()
def list_publics(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }

    client = Communicator(cookies=request.COOKIES)
    context['publics'] = client.get_public_images()

    return render(request, 'website/public_images.html', context,
        RequestContext(request))


@login_required()
def show_image_detail(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }
    project_id = kwargs['pid']
    image_id = kwargs['iid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['image'] = client.get_image(project_id=project_id,
        image_id=image_id)
    context['resource_limits'] = client.get_resourcelimits()
    volumes = client.volume_lists(project_id=project_id)
    simple_volumes = []
    for volume in volumes:
        if volume.get('app'):
            continue
        simple_volume = {}
        simple_volume['id'] = volume['id']
        simple_volume['name'] = volume['name']
        simple_volumes.append(simple_volume)
    context['volumes'] = json.dumps(simple_volumes)

    return render(request, 'website/image_detail.html', context,
        RequestContext(request))


@login_required()
def show_application_detail(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }
    project_id = kwargs['pid']
    application_id = kwargs['aid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['application'] = client.get_application(project_id=project_id,
        application_id=application_id)
    context['image'] = client.get_image(project_id=project_id,
        image_id=context['application']['image'])
    context['resource_limit'] = client.get_resourcelimit(
        context['application']['resource_limit'])

    if context['application']['is_autoscaler']:
        context['autoscaler'] = client.get_autoscaler(project_id=project_id,
        application_id=application_id)

    context['environments'] = client.get_environments(project_id=project_id,
        application_id=application_id)
    context['ports'] = client.get_ports(project_id=project_id,
        application_id=application_id)
    context['volumes'] = client.get_volume_of_application(project_id=project_id,
        app_id=application_id)
    context['pods'] = client.get_pods(project_id=project_id,
        application_id=application_id)
    context['logs'] = '\n'.join(client.get_pod_logs(project_id=project_id,
        pod_name=context['pods'][0]))
    context['mem_url'] = get_url_of_monitor_iframe('memory', context['username'],
        context['pods'][0])
    context['cpu_url'] = get_url_of_monitor_iframe('cpu', context['username'],
        context['pods'][0])

    # logger.debug(context)

    return render(request, 'website/application_detail.html', context,
        RequestContext(request))


@login_required()
def get_logs_of_pod(request, *args, **kwargs):
    project_id = kwargs['pid']
    pod = kwargs['pod']
    tail = int(request.GET.get('tail', 20))

    client = Communicator(cookies=request.COOKIES)
    response = client.get_pod_logs(project_id=project_id, pod_name=pod,
        tail=tail)
    return JsonResponse('\n'.join(response), safe=False)


@login_required()
def show_volume_detail(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }

    project_id = kwargs['pid']
    volume_id = kwargs['vid']
    client = Communicator(cookies=request.COOKIES)
    context['project'] = client.get_project(project_id=project_id)
    context['volume'] = client.get_volume(project_id=project_id,
        volume_id=volume_id)
    if context['volume']['app']:
        context['app_name'] = client.get_application(project_id,
            context['volume']['app'])['name']

    return render(request, 'website/volume_detail.html', context,
        RequestContext(request))


@login_required()
def show_public_detail(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }
    public_id = kwargs['puid']

    client = Communicator(cookies=request.COOKIES)
    context['projects'] = client.project_lists()
    context['image'] = client.get_public_image(public_id=public_id)

    return render(request, 'website/public_image_details.html', context,
        RequestContext(request))


@login_required()
@csrf_exempt
@require_POST
def clone_public_image(request, *args, **kwargs):
    puid = kwargs['puid']

    form = PublicForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": "data invalid"})

    data = {
        'pid': form.cleaned_data['project'],
        'name': form.cleaned_data['name'],
        'version': form.cleaned_data['version']
    }
    client = Communicator(cookies=request.COOKIES)
    ok = client.clone_public_image(public_id=puid, data=data)
    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


@login_required()
def user_management(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }

    if not context['is_staff']:
        return HttpResponseRedirect(reverse('dashboard'))

    client = Communicator(cookies=request.COOKIES)
    context['users'] = client.list_users()

    return render(request, 'website/user_management.html', context,
        RequestContext(request))


@login_required()
def resource_module(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }

    if not context['is_staff']:
        return HttpResponseRedirect(reverse('dashboard'))

    client = Communicator(cookies=request.COOKIES)
    context['modules'] = client.list_resource_modules()

    return render(request, 'website/resource_module.html', context,
        RequestContext(request))


@login_required()
def delete_resource_module(request, *args, **kwargs):
    module_id = kwargs['mid']

    if not kwargs['is_staff']:
        return HttpResponseRedirect(reverse('dashboard'))

    client = Communicator(cookies=request.COOKIES)
    ok = client.delete_resource_module(module_id=module_id)
    if ok:
        return HttpResponseRedirect(reverse('resource-module'))
    return HttpResponseRedirect(reverse('resource-module'))


@login_required()
@csrf_exempt
@require_POST
def create_resource_module(request, *args, **kwargs):
    if not kwargs['is_staff']:
        return JsonResponse({"error": "no permission"})

    # Check validation
    form = ResourceModuleForm(request.POST)
    if not form.is_valid():
        return JsonResponse({"error": "data invalid"})

    data = {
        'name': form.cleaned_data['name'],
        'cpu': form.cleaned_data['cpu'],
        'cpu_unit': form.cleaned_data['cpu_unit'],
        'memory': form.cleaned_data['memory'],
        'memory_unit': form.cleaned_data['memory_unit']
    }

    logger.debug(data)

    client = Communicator(cookies=request.COOKIES)
    ok = client.create_resource_module(data)
    if ok:
        return JsonResponse({"success": "success"})
    else:
        return JsonResponse({"error": "failed"})


@login_required()
def app_monitor(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }

    if not context['is_staff']:
        return HttpResponseRedirect(reverse('dashboard'))

    client = Communicator(cookies=request.COOKIES)
    context['users'] = client.list_users()
    context['monitor_base_url'] =  "http://{}/dashboard-solo/db/containers\
?fullscreen".format(settings.GRAFANA_SERVER)

    return render(request, 'website/app_monitor.html', context,
        RequestContext(request))


@login_required()
def host_monitor(request, *args, **kwargs):
    context = {
        'username': kwargs.get('username'),
        'is_staff': kwargs.get('is_staff')
    }

    if not context['is_staff']:
        return HttpResponseRedirect(reverse('dashboard'))

    client = Communicator(cookies=request.COOKIES)
    context['hosts'] = ['All Hosts']
    context['hosts'] += client.list_hosts()

    context['monitor_url'] = get_url_of_host_monitor("cpu", "All Hosts")

    return render(request, 'website/host_monitor.html', context,
        RequestContext(request))


@login_required()
def list_projects(request, *args, **kwargs):
    user_id = request.GET['user']

    client = Communicator(cookies=request.COOKIES)
    projects = client.list_projects_for_user(user_id=user_id)
    data = [{'id': project['id'], 'name': project['name']}
        for project in projects]
    return JsonResponse(data, safe=False)


@login_required()
def list_apps(request, *args, **kwargs):
    project_id = request.GET['project']

    client = Communicator(cookies=request.COOKIES)
    apps = client.list_apps_for_project(project_id=project_id)
    data = [{'id': app['id'], 'name': app['name']}
        for app in apps]
    return JsonResponse(data, safe=False)


@login_required()
def list_pods(request, *args, **kwargs):
    app_id = request.GET['app']

    client = Communicator(cookies=request.COOKIES)
    pods = client.list_pods_for_app(app_id=app_id)
    return JsonResponse(pods, safe=False)


@login_required()
@csrf_exempt
@require_POST
def test(request, *args, **kwargs):
    print(request.POST)
    if not request.FILES.get('file'):
        return JsonResponse({"error": "no file"})
    return JsonResponse({"success": "success"})
