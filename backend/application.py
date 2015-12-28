import logging, json
from threading import Thread

from django.conf import settings

from backend.models import Application, Port
from backend.kubernetes.k8sclient import KubeClient

logger = logging.getLogger('hummer')


class ApplicationBuilder(object):
    """
    ApplicationBuilder is a builder to create an appliction from an image. You
    should offer many necessary arguments.

    Parameters:
    replicas: the number of pods.
    image_name: the image name for the container.
    tcp_ports: a dict, the tcp ports of the containers. For example: {
        "http": 80, "https": 443}
    udp_ports: a dict, the udp ports of the containers.
    commands: the commands which the container runs when start.
    envs: a dict for example: {"MYSQL_HOST": "localhost", "PORT": "3306"}
    """
    kubeclient = None
    namespace = None
    application = None
    image_name = None
    replicas = 1
    tcp_ports = None
    udp_ports = None
    commands = None
    args = None
    envs = None

    def __init__(self, namespace, application, image_name, replicas=1,
        tcp_ports=None, udp_ports=None, commands=None, args=None, envs=None):
        self.kubeclient = KubeClient("http://{}:{}{}".format(settings.MASTER_IP,
            settings.K8S_PORT, settings.K8S_API_PATH))

        self.namespace = namespace
        self.application = application
        self.image_name = image_name
        self.replicas = replicas
        self.tcp_ports = tcp_ports
        self.udp_ports = udp_ports
        self.commands = commands
        self.args = args
        self.envs = envs

    def create_application(self):
        """
        Create application by multiple threading.
        """
        creating_thread = Thread(target=target)
        creating_thread.start()

    def _create_application(self):
        """
        First create a replicationcontroller, then create a service, update
        database at last.
        """
        logger.info('Create an application {} in namespace {} by image {}.'
            .format(self.application.name, self.namespace, self.image_name))


    def _create_controller(self):
        """
        Create a replicationcontroller by provided image.
        """
        pass

    def _create_service(self):
        """
        Create a service on the replicationcontroller.
        """
        pass

