import logging, json
from threading import Thread

from django.conf import settings

from backend.models import Application, Port
from backend.kubernetes.k8sclient import KubeClient
from backend.schedule import DockerSchedulerFactory
from backend.utils import get_optimal_docker_host

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

    def __init__(self, namespace, application, image_name, tcp_ports=None,
        udp_ports=None, commands=None, args=None, envs=None, is_public=False):
        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))

        self.namespace = namespace
        self.application = application
        self.image_name = image_name
        self.tcp_ports = tcp_ports
        self.udp_ports = udp_ports
        self.commands = commands
        self.args = args
        self.envs = envs
        self.is_public = is_public

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
            .format(self.application.name, self.namespace, self.image_name))

        if not self._create_controller():
            logger.debug('Create controller {} failed.'.format(
                self.application.name))
            logger.info('Create an application {} in namespace {} failed.'
            .format(self.application.name, self.namespace, self.image_name))

            self._update_application_metadata(status='error')
            return None

        if not self._create_service():
            logger.debug('Create service {} failed.'.format(
                self.application.name))
            logger.info('Create an application {} in namespace {} failed.'
            .format(self.application.name, self.namespace, self.image_name))

            self._update_application_metadata(status='error')
            return None

        # update metadata
        internal_ip, ports = self._get_service_ip_and_ports()
        if self.is_public:
            external_ip = get_optimal_docker_host()
            self._update_application_metadata(status='active',
                internal_ip=internal_ip,
                external_ip=external_ip
            )
        else:
            self._update_application_metadata(status='active',
                internal_ip=internal_ip
            )

        # create port metadata
        self._create_ports_metadata(ports)

    def _create_controller(self):
        """
        Create a replicationcontroller by provided image.
        """
        return self.kubeclient.create_controller(namespace=self.namespace,
            name=self.application.name,
            image_name=self.image_name,
            replicas=self.application.replicas,
            tcp_ports=self.tcp_ports,
            udp_ports=self.udp_ports,
            commands=self.commands,
            args=self.args,
            envs=self.envs
        )

    def _create_service(self):
        """
        Create a service on the replicationcontroller.
        """
        return self.kubeclient.create_service(namespace=self.namespace,
            name=self.application.name,
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
            self.application.name)
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
        for port_dict in ports:
            port = Port(app=self.application,
                name=port_dict['name'],
                protocol=port_dict['protocol'],
                external_port=port_dict.get('nodePort', None),
                internal_port=port_dict['port']
            )
            port.save()


class ApplicationDestroy(object):
    """
    ApplicationDestroy is to destroy application instance, including controller
    and service.
    """
    application = None

    def __init__(self, application):
        self.application = application
        self.namespace = self.application.image.project.user.username
        self.service_name = self.application.name
        self.controller_name = self.application.name

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
        self._delete_application_metadata()
        self._delete_port_metadata()

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
        logger.debug("delete application medatade.")
        self.application.delete()

    def _delete_port_metadata(self):
        logger.debug("delete port metadata.")
        ports = Port.objects.filter(app=self.application)
        for port in ports:
            logger.debug("delete port {} metadata.".format(port.name))
            port.delete()

