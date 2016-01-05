import unittest
import os

from backend.nfs import NFSClient

class NFSClientTestCase(unittest.TestCase):

    def setUp(self):
        self.client = NFSClient('192.168.0.15', 22, 'wangtao', 'admin123')

    def tearDown(self):
        self.client.close()

    def test_makedir(self):
        self.client.makedir('/home/wangtao/testdir')

    def test_removedir(self):
        self.client.removedir('/home/wangtao/testdir')

    def test_copy_file_to_remote(self):
        res = self.client.copy_file_to_remote("/home/wangtao/images/nginx.tar",
            "/home/wangtao/nginx.tar")
        print(res)

    def test_copy_file_to_local(self):
        res = self.client.copy_file_to_local("/home/wangtao/nfs_install.sh",
            "/home/wangtao/nfs_install.sh")
        print(res)

    def test_tar_and_copy_to_local(self):
        self.client.tar_and_copy_to_local("/hummer/test", "/home/wangtao/test/test.tar")

    def test_copy_file_to_remote_and_untar(self):
        self.client.copy_file_to_remote_and_untar("/home/wangtao/test/test.tar",
            "/hummer/test")
