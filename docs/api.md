/api/users
/api/users/{id}

/api/projects
POST: user, name, desc
/api/projects/{project_id}

/api/projects/{project_id}/images
POST: project(path), name, desc, version, is_public, is_image(0/1/2, if 1, attach old_image_name and old_image_version), file
/api/projects/{project_id}/images/{image_id}

/api/projects/{project_id}/applications
POST(json): image, name, replicas, is_public, session_affinity, ports, commands, args, envs
/api/projects/{project_id}/applications/{app_id}

/api/projects/{project_id}/applications/{app_id}/ports
/api/projects/{project_id}/applications/{app_id}/ports/{port_id}


For example:
1. create image
image file:
http -a user:user123 -f POST http://127.0.0.1:8000/api/projects/1/images/ name="nginx" desc="nginx" version="1.9.9" is_public=false is_image=1 old_image_name="nginx" old_image_version="1.9.9" file@/home/wangtao/images/nginx.tar >abc.html
snapshot:
http -a user:user123 -f POST http://127.0.0.1:8000/api/projects/1/images/ name="my-nginx" desc="my-nginx" version="1.9.9" is_public=false is_image=2 file@/home/wangtao/images/nginxn.tar >abc.html

2. delete image
http -a user:user123 DELETE http://127.0.0.1:8000/api/projects/1/images/3/

3. create application
http -a user:user123 POST http://127.0.0.1:8000/api/projects/1/applications/ <data.json >abc.html

data.json:
{
    "image": 12,
    "name": "nginx",
    "replicas": 2,
    "is_public": false,
    "session_affinity": false,
    "ports": [
        {"name": "http", "port": 80, "protocol": "TCP"}
    ]
}

4. delete application
http -a user:user123 DELETE http://127.0.0.1:8000/api/projects/1/applications/11/ >abc.html
