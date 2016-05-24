import logging, json
from threading import Thread

from django.conf import settings

from backend.models import Application, Port, Volume, AutoScaler, Environment
from backend.kubernetes.k8sclient import KubeClient
from backend.utils import (get_optimal_docker_host, get_optimal_external_ip,
    get_application_instance_name)

logger = logging.getLogger('hummer')


class ApplicationBuilder(object):
    """
    ApplicationBuilder is a builder to create an appliction from an image. You
    should offer many necessary arguments.

    Parameters:
    image_name: the image name for the container.
    tcp_ports: a dict, the tcp ports of the containers. For example: {
        "http": 80, "https": 443}
    udp_ports: a dict, the udp ports of the containers.
    commands: the commands which the container runs when start.
    envs: a dict for example: {"MYSQL_HOST": "localhost", "PORT": "3306"}
    volumes: a dict, for example: [{"volume": id, "mount_path": path}]
    """
    namespace = None
    application = None
    image_name = None
    tcp_ports = None
    udp_ports = None
    commands = None
    args = None
    envs = None
    is_public = False
    volumes = None

    def __init__(self, application, image_name, tcp_ports=None,
        udp_ports=None, commands=None, args=None, envs=None, is_public=False,
        volumes=None, min_replicas=None, max_replicas=None, cpu_target=None):
        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))

        self.application = application
        self.namespace = self.application.image.project.name
        self.application_name = get_application_instance_name(self.application)
        self.image_name = image_name
        self.tcp_ports = tcp_ports
        self.udp_ports = udp_ports
        self.commands = commands
        self.args = args
        self.envs = envs
        self.is_public = is_public
        self.volumes = volumes

        # Compute the resource limit of the application
        resource_limit = self.application.resource_limit
        self.cpu = str(resource_limit.cpu) + resource_limit.cpu_unit
        self.memory = str(resource_limit.memory) + resource_limit.memory_unit

        # autoscaler
        if self.application.is_autoscaler:
            self.min_replicas = int(min_replicas)
            self.max_replicas = int(max_replicas)
            self.cpu_target = int(cpu_target)
            logger.debug(str(self.min_replicas) + " " + str(self.max_replicas)
                + " " + str(self.cpu_target))

    def create_application(self):
        """
        Create application by multiple threading.
        """
        creating_thread = Thread(target=self._create_application)
        creating_thread.start()

    def _create_application(self):
        """
        First create a replicationcontroller, then create a service, update
        database at last.
        """
        logger.info('Create an application {} in namespace {} by image {}.'
            .format(self.application_name, self.namespace, self.image_name))

        if not self._create_controller():
            logger.debug('Create controller {} failed.'.format(
                self.application_name))
            logger.info('Create an application {} in namespace {} failed.'
            .format(self.application_name, self.namespace, self.image_name))

            self._update_application_metadata(status='error')
            return None

        if self.tcp_ports or self.udp_ports:
            if not self._create_service():
                logger.debug('Create service {} failed.'.format(
                    self.application_name))
                logger.info('Create an application {} in namespace {} failed.'
                .format(self.application_name, self.namespace, self.image_name))

                self._update_application_metadata(status='error')
                return None
            internal_ip, ports = self._get_service_ip_and_ports()
        else:
            internal_ip = None
            ports = None

        # update metadata
        if self.is_public:
            external_ip = get_optimal_external_ip(namespace=self.namespace,
                app_name=self.application_name)
            self._update_application_metadata(status='active',
                internal_ip=internal_ip,
                external_ip=external_ip
            )
        else:
            self._update_application_metadata(status='active',
                internal_ip=internal_ip
            )

        # mount volume
        self._mount_volume_onto_application()

        # create port metadata
        self._create_ports_metadata(ports)

        # create environment metadata
        self._create_environments_metadata()

        # create autoscaler
        if self.application.is_autoscaler:
            scaler_builder = AutoScalerBuilder(
                application=self.application,
                min_replicas=self.min_replicas,
                max_replicas=self.max_replicas,
                cpu_target=self.cpu_target
            )
            scaler_builder.create_autoscaler()

    def _create_controller(self):
        """
        Create a replicationcontroller by provided image.
        """
        return self.kubeclient.create_controller(namespace=self.namespace,
            name=self.application_name,
            image_name=self.image_name,
            cpu=self.cpu,
            memory=self.memory,
            replicas=self.application.replicas,
            tcp_ports=self.tcp_ports,
            udp_ports=self.udp_ports,
            commands=self.commands,
            args=self.args,
            envs=self.envs,
            volumes=self._get_volume_names_and_path()
        )

    def _create_service(self):
        """
        Create a service on the replicationcontroller.
        """
        return self.kubeclient.create_service(namespace=self.namespace,
            name=self.application_name,
            tcp_ports=self.tcp_ports,
            udp_ports=self.udp_ports,
            is_public=self.is_public,
            session_affinity=self.application.session_affinity
        )

    def _get_service_ip_and_ports(self):
        """
        Get internal_ip and ports of the service.
        """
        response = self.kubeclient.get_service_details(self.namespace,
            self.application_name)
        return (response['spec']['clusterIP'], response['spec']['ports'])

    def _update_application_metadata(self, status=None, internal_ip=None,
        external_ip=None):
        """
        Update the application metadata.
        """
        if status:
            self.application.status = status
        if internal_ip:
            self.application.internal_ip = internal_ip
        if external_ip:
            self.application.external_ip = external_ip

        self.application.save()

    def _create_ports_metadata(self, ports):
        """
        Create ports metadata for application.
        """
        if not ports:
            return None

        for port_dict in ports:
            port = Port(app=self.application,
                name=port_dict['name'],
                protocol=port_dict['protocol'],
                external_port=port_dict.get('nodePort', None),
                internal_port=port_dict['port']
            )
            port.save()

    def _create_environments_metadata(self):
        """
        Create environment metadata for application.
        """
        if not self.envs:
            return None

        for name, value in self.envs.items():
            env = Environment(app=self.application,
                name=name, value=value)
            env.save()

    def _mount_volume_onto_application(self):
        """
        Edit the metadata, Mount volumes onto this application.
        """
        if not self.volumes:
            return None
        for volume_item in self.volumes:
            volume = Volume.objects.get(id=volume_item['volume'])
            logger.debug("mount volume {} onto application {}.".format(
                volume.name, self.application_name))
            volume.app = self.application
            volume.mount_path = volume_item['mount_path']
            volume.save()

    def _get_volume_names_and_path(self):
        """
        Return the volume names from volume ids. The true volume instance name
        is "project_name-volume_name".
        """
        if not self.volumes:
            return None
        volume_name_path = {}
        for volume_item in self.volumes:
            volume = Volume.objects.get(id=int(volume_item['volume']))
            volume_name = "{}-{}-{}".format(self.namespace,
                volume.project.name, volume.name)
            volume_name_path[volume_name] = volume_item['mount_path']
        logger.debug(volume_name_path)
        return volume_name_path


class ApplicationDestroyer(object):
    """
    ApplicationDestroyer is to destroy application instance, including controller
    and service.
    """
    application = None

    def __init__(self, application):
        self.application = application
        self.application_name = get_application_instance_name(self.application)
        self.namespace = self.application.image.project.name
        self.service_name = self.application_name
        self.controller_name = self.application_name

        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))

    def destroy_application_instance(self):
        """
        Destroy application instance by multiple threading.
        """
        deleting_thread = Thread(target=self._destroy_application_instance)
        deleting_thread.start()

    def _destroy_application_instance(self):
        self._update_application_status(status='deleting')

        if not self._destroy_service_instance():
            logger.debug("Delete service {} failed.".format(self.service_name))

        if not self._destroy_controller_instance():
            logger.debug("Delete controller {} failed.".format(
                self.controller_name))

        if not self._destroy_pods_instance():
            logger.debug("Delete pods with label 'app={}' failed.".format(
                self.controller_name))

        self._update_application_status(status='deleted')
        self._umount_volume()

        # delete autoscaler
        if self.application.is_autoscaler:
            autoscaler_destroyer = AutoScalerDestroyer(self.application)
            autoscaler_destroyer.delete_autoscaler()

        self._delete_application_metadata()
        self._delete_port_metadata()
        self._delete_environments()

    def _destroy_service_instance(self):
        return self.kubeclient.delete_service(namespace=self.namespace,
                name=self.service_name)

    def _destroy_controller_instance(self):
        return self.kubeclient.delete_controller(namespace=self.namespace,
                name=self.controller_name)

    def _destroy_pods_instance(self):
        pods = self.kubeclient.list_pods(namespace=self.namespace,
            label="app={}".format(self.controller_name))
        logger.debug(pods)

        res = True
        for pod in pods:
            flag = self.kubeclient.delete_pod(namespace=self.namespace,
                name=pod)
            if not flag:
                res = False
        return res

    def _update_application_status(self, status):
        self.application.status = status
        self.application.save()

    def _delete_application_metadata(self):
        logger.debug("delete application medatada.")
        self.application.delete()

    def _delete_port_metadata(self):
        logger.debug("delete port metadata.")
        ports = Port.objects.filter(app=self.application)
        for port in ports:
            logger.debug("delete port {} metadata.".format(port.name))
            port.delete()

    def _delete_environments(self):
        envs = Environment.objects.filter(app=self.application)
        for env in envs:
            env.delete()

    def _umount_volume(self):
        """
        Umount volumes which mounted on application.
        """
        volumes = Volume.objects.filter(app=self.application)
        for volume in volumes:
            logger.debug("umount volume {}-{} from application {}.".format(
                volume.project.name, volume.name, self.application_name))
            volume.app = None
            volume.mount_path = None
            volume.save()


class AutoScalerBuilder(object):
    """
    AutoScalerBuilder is a builder to create an autoscaler for application. You
    should offer many necessary arguments.

    Parameters:
    min_replicas, max_replicas, cpu_target: integer parameters, -1 represents
    infinite big value.
    """
    def __init__(self, application, min_replicas=-1, max_replicas=-1,
        cpu_target=-1):
        self.application = application
        self.application_name = get_application_instance_name(self.application)
        self.namespace = self.application.image.project.name
        self.min_replicas = min_replicas
        self.max_replicas = max_replicas
        self.cpu_target = cpu_target

        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_V1BETA1_API_PATH))

    def create_autoscaler(self):
        """
        Create autoscaler instance for application by multiple threading.
        """
        creating_thread = Thread(target=self._create_autoscaler_instance)
        creating_thread.start()

    def _create_autoscaler_instance(self):
        ok = self.kubeclient.create_autoscaler(
            namespace=self.namespace,
            name=self.application_name,
            minReplicas=self.min_replicas,
            maxReplicas=self.max_replicas,
            cpu_target=self.cpu_target)
        if not ok:
            logger.error("Create autoscaler {} failed.".format(
                self.application_name))
            return None
        logger.debug("Create autoscaler {} successfully.".format(
            self.application_name))

        scaler = AutoScaler(app=self.application,
            min_replicas=self.min_replicas,
            max_replicas=self.max_replicas,
            cpu_target=self.cpu_target)
        scaler.save()


class AutoScalerDestroyer(object):
    """
    AutoScalerDestroyer is to destroy autoscaler instance when deleting
    application.
    """
    def __init__(self, application):
        self.application = application
        self.application_name = get_application_instance_name(self.application)
        self.namespace = self.application.image.project.name

        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_V1BETA1_API_PATH))

    def delete_autoscaler(self):
        """
        Destroy autoscaler for application instance by multiple threading.
        """
        deleting_thread = Thread(target=self._delete_autoscaler_instance)
        deleting_thread.start()

    def _delete_autoscaler_instance(self):
        scalers = AutoScaler.objects.filter(app=self.application)
        for scaler in scalers:
            scaler.delete()

        ok = self.kubeclient.delete_autoscaler(namespace=self.namespace,
            name=self.application_name)
        if not ok:
            logger.error("Delete autoscaler {} failed.".format(
                self.application_name))
        else:
            logger.debug("Delete autoscaler {} successfully.".format(
                self.application_name))

