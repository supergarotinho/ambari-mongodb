import os
import sys
from time import sleep

# Ambari includes
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management.libraries.script import Script

# Custom service test classes includes
from integrated_base_test import IntegratedBaseTestCase

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(SCRIPT_DIR, '../scripts/')
SERVICE_DIR = os.path.join(SCRIPT_DIR, '../')
sys.path.append(PACKAGE_DIR)
sys.path.append(SERVICE_DIR)

# Custom service scripts includes
import params
from mongos import MongosServer
from mongo_base import InstanceConfig
from mongo_base import InstanceStatus
from mongo_config import MongoConfigServer

class IntegratedMongoConfTestCase(IntegratedBaseTestCase):

    def setUp(self):
        self.as_super = super(IntegratedMongoConfTestCase, self)
        self.as_super.setUp()
        self.config_server = None
        params.try_interval = 4
        params.times_to_try = 2
        # Configuring and Installing mongo config dependencies
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'
        server.configure(self.env)
        server.install(self.env)
        # Configuring and Installing mongos dependencies
        server = MongosServer()
        server.my_hostname = 'node1.test.com'
        server.configure(self.env)
        server.install(self.env)

    def tearDown(self):
        self.as_super = super(IntegratedMongoConfTestCase, self)
        self.as_super.tearDown()
        if self.config_server:
            self.config_server.stop(self.env)

    def several_hosts_setup(self):
        Script.config['clusterHostInfo'] = {
            'mongos_hosts': ['node1.test.com','node2.test.com'],
            'mongodb_hosts': [],
            'mongodc_hosts': ['node1.test.com','node2.test.com','node3.test.com']
        }

        params.mongos_cluster_definition = ''

    def several_hosts_setup_with_config_server(self):
        Script.config['clusterHostInfo'] = {
            'mongos_hosts': ['node1.test.com','node2.test.com'],
            'mongodb_hosts': [],
            'mongodc_hosts': ['node1.test.com']
        }

        params.mongos_cluster_definition = ''

        # Starting the required config server
        self.config_server = MongoConfigServer()
        self.config_server.my_hostname = 'node1.test.com'
        self.config_server.start(self.env)

    expected_cluster_status_for_several_hosts_stopped = [
        ('0',['node1.test.com','node2.test.com'], [
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node1_0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_0_0',
                           log_file='/var/log/mongodb/node1_0_0.log',
                           db_port='27017',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node2_0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_0_0',
                           log_file='/var/log/mongodb/node2_0_0.log',
                           db_port='27017',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None)])]

    def one_host_setup(self):
        Script.config['clusterHostInfo'] = {
            'mongos_hosts': ['node1.test.com'],
            'mongodb_hosts': [],
            'mongodc_hosts': ['node1.test.com']
        }

        params.mongos_cluster_definition = 'node1.test.com,node1.test.com'

        self.config_server = MongoConfigServer()
        self.config_server.my_hostname = 'node1.test.com'
        self.config_server.start(self.env)

    expected_cluster_status_for_one_host_stopped = [
        ('0',['node1.test.com','node1.test.com'], [
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node1_0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_0_0',
                           log_file='/var/log/mongodb/node1_0_0.log',
                           db_port='27017',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node1_0_1.pid',
                           final_db_path='/var/lib/mongodb/node1_0_1',
                           log_file='/var/log/mongodb/node1_0_1.log',
                           db_port='27018',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None)])]

    def test_get_cluster_data_with_one_host(self):
        self.one_host_setup()
        server = MongosServer()
        server.my_hostname = 'node1.test.com'

        expectedClusterData = [('0', ['node1.test.com', 'node1.test.com'],
                                [InstanceConfig(shard_name='0',
                                                pid_file_name='/var/run/mongodb/node1_0_0.pid',
                                                final_db_path='/var/lib/mongodb/node1_0_0',
                                                log_file='/var/log/mongodb/node1_0_0.log',
                                                db_port='27017',
                                                host_name='node1.test.com',
                                                is_arbiter=False),
                                 InstanceConfig(shard_name='0',
                                                pid_file_name='/var/run/mongodb/node1_0_1.pid',
                                                final_db_path='/var/lib/mongodb/node1_0_1',
                                                log_file='/var/log/mongodb/node1_0_1.log',
                                                db_port='27018',
                                                host_name='node1.test.com',
                                                is_arbiter=False)])]
        clusterData = server.getClusterData()
        self.assertEqual(clusterData,expectedClusterData,"The cluster data for the mongos is not right")

    def test_get_cluster_status_with_one_host(self):
        self.one_host_setup()
        server = MongosServer()
        server.my_hostname = 'node1.test.com'

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus,self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result before stating the mongos is not right")

    def test_stopping_an_already_stopped_cluster(self):
        self.one_host_setup()
        server = MongosServer()
        server.my_hostname = 'node1.test.com'
        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus,self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result before stating the mongos is not right")
        server.stop(self.env)
        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result after stopping the mongos is not right")

    def test_mongos_in_one_host(self):
        self.one_host_setup()

        server = MongosServer()
        server.my_hostname = 'node1.test.com'

        with self.assertRaises(ComponentIsNotRunning):
            server.status(self.env)

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result before stating the mongos is not right")

        server.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server.status(self.env)

        expectedClusterStatus = [('0', ['node1.test.com', 'node1.test.com'], [
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node1_0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_0_0',
                           log_file='/var/log/mongodb/node1_0_0.log',
                           db_port='27017',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None),
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node1_0_1.pid',
                           final_db_path='/var/lib/mongodb/node1_0_1',
                           log_file='/var/log/mongodb/node1_0_1.log',
                           db_port='27018',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None)])]
        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatus,"The cluster status result for a started mongos is "
                                                              "not right")

        server.stop(self.env)

        with self.assertRaises(ComponentIsNotRunning):
            server.status(self.env)

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result after stopping the mongos is not right")

    def test_get_cluster_status_with_several_hosts(self):
        self.several_hosts_setup_with_config_server()
        server = MongosServer()
        server.my_hostname = 'node1.test.com'

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the mongos is not right")


    def test_mongos_with_several_hosts(self):
        self.several_hosts_setup_with_config_server()

        server2 = MongosServer()
        server2.my_hostname = 'node2.test.com'
        server1 = MongosServer()
        server1.my_hostname = 'node1.test.com'

        clusterStatus = server2.getClusterStatus(server2.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the mongos is not right")

        server2.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server2.status(self.env)

        expectedClusterStatusServer2On = [
        ('0',['node1.test.com','node2.test.com'], [
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node1_0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_0_0',
                           log_file='/var/log/mongodb/node1_0_0.log',
                           db_port='27017',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node2_0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_0_0',
                           log_file='/var/log/mongodb/node2_0_0.log',
                           db_port='27017',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None)])]

        clusterStatus = server2.getClusterStatus(server2.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatusServer2On, "The cluster status result for a started node2"
                                                                        " in the mongos is not right")
        server1.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server1.status(self.env)

        expectedClusterStatusServer1On = [
        ('0',['node1.test.com','node2.test.com'], [
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node1_0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_0_0',
                           log_file='/var/log/mongodb/node1_0_0.log',
                           db_port='27017',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None),
            InstanceStatus(shard_name='0',
                           pid_file_name='/var/run/mongodb/node2_0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_0_0',
                           log_file='/var/log/mongodb/node2_0_0.log',
                           db_port='27017',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None)])]

        clusterStatus = server1.getClusterStatus(server1.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatusServer1On, "The cluster status result for a started node1"
                                                                        " in the mongos is not right")

        server2.stop(self.env)
        with self.assertRaises(ComponentIsNotRunning):
            server2.status(self.env)

        server1.stop(self.env)
        with self.assertRaises(ComponentIsNotRunning):
            server1.status(self.env)

        clusterStatus = server2.getClusterStatus(server2.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result after stopping the mongos is not right")

    def test_must_not_start_if_all_config_servers_are_off(self):
        self.several_hosts_setup()

        server1 = MongosServer()
        server1.my_hostname = 'node1.test.com'

        clusterStatus = server1.getClusterStatus(server1.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the mongos is not right")

        server1.start(self.env)

        clusterStatus = server1.getClusterStatus(server1.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the mongos is not right")


    def test_must_not_start_if_no_config_servers_primary_on(self):
        self.several_hosts_setup()

        server1 = MongosServer()
        server1.my_hostname = 'node1.test.com'

        clusterStatus = server1.getClusterStatus(server1.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the mongos is not right")

        # Starting only the secondary config servers
        config_server2 = MongoConfigServer()
        config_server2.my_hostname = 'node2.test.com'
        config_server2.start(self.env)

        config_server3 = MongoConfigServer()
        config_server3.my_hostname = 'node3.test.com'
        config_server3.start(self.env)

        server1.start(self.env)

        clusterStatus = server1.getClusterStatus(server1.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the mongos is not right")
