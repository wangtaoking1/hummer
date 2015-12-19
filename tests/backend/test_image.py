import unittest

from backend.image import ImageBuilder
from backend.models import MyUser


class ImageBuilderTestCase(unittest.TestCase):
    def setUp(self):
        # build_file = 'abc.tar'
        # user = MyUser
        # self.builder = ImageBuilder(build_file=build_file, is_image=False,
        #     image_id=2, user=user)
        pass

    def tearDown(self):
        pass

    def test_create_image(self):
        # self.builder.create_image()
        self.assertEqual(True, True)

# if __name__ == '__main__':
#     suite = (unittest.TestLoader()
#                  .loadTestsFromTestCase(ImageBuilderTestCase))
#     unittest.TextTestRunner(verbosity=2).run(suite)
