/api/users
/api/users/{id}

/api/projects
POST: user, name, desc
/api/projects/{project_id}

/api/projects/{project_id}/images
POST: project(path), name, desc, version, is_public, is_image(0/1/2), file
/api/projects/{project_id}/images/{image_id}

/api/projects/{project_id}/applications
POST(json): image, name, replicas, is_public, session_affinity, ports, commands, args, envs
/api/projects/{project_id}/applications/{app_id}

/api/projects/{project_id}/applications/{app_id}/ports
/api/projects/{project_id}/applications/{app_id}/ports/{port_id}
