import unittest

from backend.application import ApplicationBuilder, AutoScalerBuilder
from backend.models import Application


class ApplicationBuilderTestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_application(self):
        pass

    def test_create_autoscaler(self):
        app = Application.objects.get(id=17)
        builder = AutoScalerBuilder(application=app, min_replicas=1,
            max_replicas=5, cpu_target=30)
        builder.create_autoscaler()

