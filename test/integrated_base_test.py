import unittest
import os

from resource_management.core.environment import Environment

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(SCRIPT_DIR, '../package/scripts/')
SERVICE_DIR = os.path.join(SCRIPT_DIR, '../')

class IntegratedBaseTestCase(unittest.TestCase):

    SLEEP_INTERVAL_AFTER_START_A_INSTANCE = 5

    @classmethod
    def setUpClass(cls):
        IntegratedBaseTestCase.env = Environment(SERVICE_DIR, tmp_dir=SERVICE_DIR)
        IntegratedBaseTestCase.env.__enter__()

    @classmethod
    def tearDownClass(cls):
        IntegratedBaseTestCase.env.__exit__(None,None,None)

    def setUp(self):
        self.configureHosts()

    def tearDown(self):
        self.cleanHosts()
        self.removeDirs()

    def removeDirs(self):
        for host in self.getHosts().keys():
            name = host.split('.')[0]
            command_str = 'rm -rf /var/lib/mongodb/' + name + '_*'
            os.system(command_str)
            command_str = 'rm -rf /var/log/mongodb/' + name + '_*'
            os.system(command_str)

    def getHosts(self):
        """

        :return: The hosts in the cluster
        :rtype dict
        """
        return {'node1.test.com': '127.69.0.1',
                'node2.test.com': '127.69.0.2',
                'node3.test.com': '127.69.0.3'}

    def configureHosts(self):
        """
        Change the local hosts file to add the hosts with local ips (/etc/hosts)

        :type hosts: dict
        :param hosts: A dictionary with 'host_name': 'ip' values
        :return: None
        """
        for key, value in self.getHosts().iteritems():
            command_str = 'echo "' + value + ' ' + key + '" >> /etc/hosts'
            os.system(command_str)

    def cleanHosts(self):
        """
        Clean the modifications made on /etc/hosts file made for testing

        :return: None
        """
        command_str = "cat /etc/hosts | sed '/\.test\.com/D' > /tmp/hosts"
        os.system(command_str)
        command_str = "cat /tmp/hosts > /etc/hosts"
        os.system(command_str)