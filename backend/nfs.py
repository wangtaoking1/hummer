import os
import logging

import paramiko

logger = logging.getLogger('hummer')


class NFSClient(object):
    """
    NFSClient is a connector of the nfs server, and can make some operators.
    """
    client = None

    def __init__(self, server, port, user, password):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.client.connect(server, port, user, password)
        except Exception as e:
            logger.debug(e)

    def makedir(self, path):
        """
        Make direction on nfs server.
        """
        stdin, stdout, stderr = self.client.exec_command("mkdir -p " + path)
        for line in stderr:
            logger.debug(line)

    def removedir(self, path):
        """
        Remove direction on nfs server.
        """
        stdin, stdout, stderr = self.client.exec_command("rm -r " + path)
        for line in stderr:
            logger.debug(line)

    def copy_file_to_remote(self, localfile, remotefile):
        """
        Copy localfile to remote nfs server, like scp command.
        """
        sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())
        sftp = self.client.open_sftp()
        try:
            sftp.put(localfile, remotefile)
        except Exception as e:
            logger.debug(e)
            return False
        return True

    def copy_file_to_local(self, remotefile, localfile):
        """
        Copy remote file to local filesystem, like scp command.
        """
        sftp = paramiko.SFTPClient.from_transport(self.client.get_transport())
        sftp = self.client.open_sftp()
        try:
            sftp.get(remotefile, localfile)
        except Exception as e:
            logger.debug(e)
            return False
        return True

    def tar_and_copy_to_local(self, remotedir, localfile):
        """
        Tar remotedir as a package, and copy to local.
        """
        pass

    def copy_file_to_remote_and_untar(self, localfile, remotedir):
        """
        Copy local tar file to remote, and untar into the remote dir.
        """
        pass

    def close(self):
        self.client.close()
