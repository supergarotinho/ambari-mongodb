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
from mongo_config import MongoConfigServer
from mongo_base import InstanceConfig
from mongo_base import InstanceStatus

class IntegratedMongoConfTestCase(IntegratedBaseTestCase):

    def setUp(self):
        self.as_super = super(IntegratedMongoConfTestCase, self)
        self.as_super.setUp()
        params.try_interval = 4
        params.times_to_try = 2
        # Configuring and Installing mongo config dependencies
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'
        server.configure(self.env)
        server.install(self.env)

    def several_hosts_setup(self):
        Script.config['clusterHostInfo'] = {
            'mongos_hosts': [],
            'mongodb_hosts': [],
            'mongodc_hosts': ['node1.test.com','node2.test.com','node3.test.com']
        }

        params.mongoconf_cluster_definition = ''

    expected_cluster_status_for_several_hosts_stopped = [
        ('configReplSet0',['node1.test.com','node2.test.com','node3.test.com'], [
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_0',
                           log_file='/var/log/mongodb/node1_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node2_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_configReplSet0_0',
                           log_file='/var/log/mongodb/node2_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node3_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_configReplSet0_0',
                           log_file='/var/log/mongodb/node3_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None)])]

    def one_host_setup(self):
        Script.config['clusterHostInfo'] = {
            'mongos_hosts': [],
            'mongodb_hosts': [],
            'mongodc_hosts': ['node1.test.com']
        }

        params.mongoconf_cluster_definition = 'node1.test.com,node1.test.com,node1.test.com'

    expected_cluster_status_for_one_host_stopped = [
        ('configReplSet0',['node1.test.com','node1.test.com','node1.test.com'], [
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_0',
                           log_file='/var/log/mongodb/node1_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_1.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_1',
                           log_file='/var/log/mongodb/node1_configReplSet0_1.log',
                           db_port='27020',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_2.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_2',
                           log_file='/var/log/mongodb/node1_configReplSet0_2.log',
                           db_port='27021',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None)])]

    def test_get_cluster_data_with_one_host(self):
        self.one_host_setup()
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'

        expectedClusterData = [('configReplSet0', ['node1.test.com', 'node1.test.com', 'node1.test.com'],
                                [InstanceConfig(shard_name='configReplSet0',
                                                pid_file_name='/var/run/mongodb/node1_configReplSet0_0.pid',
                                                final_db_path='/var/lib/mongodb/node1_configReplSet0_0',
                                                log_file='/var/log/mongodb/node1_configReplSet0_0.log',
                                                db_port='27019',
                                                host_name='node1.test.com',
                                                is_arbiter=False),
                                 InstanceConfig(shard_name='configReplSet0',
                                                pid_file_name='/var/run/mongodb/node1_configReplSet0_1.pid',
                                                final_db_path='/var/lib/mongodb/node1_configReplSet0_1',
                                                log_file='/var/log/mongodb/node1_configReplSet0_1.log',
                                                db_port='27020',
                                                host_name='node1.test.com',
                                                is_arbiter=False),
                                 InstanceConfig(shard_name='configReplSet0',
                                                pid_file_name='/var/run/mongodb/node1_configReplSet0_2.pid',
                                                final_db_path='/var/lib/mongodb/node1_configReplSet0_2',
                                                log_file='/var/log/mongodb/node1_configReplSet0_2.log',
                                                db_port='27021',
                                                host_name='node1.test.com',
                                                is_arbiter=False)])]
        clusterData = server.getClusterData()
        self.assertEqual(clusterData,expectedClusterData,"The cluster data for the replicaset is not right")

    def test_get_cluster_status_with_one_host(self):
        self.one_host_setup()
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus,self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result before stating the replicaset is not right")

    def test_stopping_an_already_stopped_cluster(self):
        self.one_host_setup()
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'
        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus,self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result before stating the replicaset is not right")
        server.stop(self.env)
        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result after stopping the replicaset is not right")

    def test_replicaset_in_one_host(self):
        self.one_host_setup()

        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'

        with self.assertRaises(ComponentIsNotRunning):
            server.status(self.env)

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result before stating the replicaset is not right")

        server.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server.status(self.env)

        expectedClusterStatus = [('configReplSet0', ['node1.test.com', 'node1.test.com', 'node1.test.com'], [
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_0',
                           log_file='/var/log/mongodb/node1_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="PRIMARY"),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_1.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_1',
                           log_file='/var/log/mongodb/node1_configReplSet0_1.log',
                           db_port='27020',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY"),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_2.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_2',
                           log_file='/var/log/mongodb/node1_configReplSet0_2.log',
                           db_port='27021',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY")])]
        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatus,"The cluster status result for a started replicaset is "
                                                              "not right")

        server.stop(self.env)

        with self.assertRaises(ComponentIsNotRunning):
            server.status(self.env)

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_one_host_stopped,
                         "The cluster status result after stopping the replicaset is not right")

    def test_get_cluster_status_with_several_hosts(self):
        self.several_hosts_setup()
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'

        clusterStatus = server.getClusterStatus(server.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the replicaset is not right")


    def test_replicaset_with_several_hosts(self):
        self.several_hosts_setup()

        server3 = MongoConfigServer()
        server3.my_hostname = 'node3.test.com'
        server2 = MongoConfigServer()
        server2.my_hostname = 'node2.test.com'
        server1 = MongoConfigServer()
        server1.my_hostname = 'node1.test.com'

        clusterStatus = server3.getClusterStatus(server3.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result before stating the replicaset is not right")

        server3.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server3.status(self.env)

        expectedClusterStatusServer3On = [
        ('configReplSet0',['node1.test.com','node2.test.com','node3.test.com'], [
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_0',
                           log_file='/var/log/mongodb/node1_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node2_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_configReplSet0_0',
                           log_file='/var/log/mongodb/node2_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node3_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_configReplSet0_0',
                           log_file='/var/log/mongodb/node3_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None)])]

        clusterStatus = server3.getClusterStatus(server3.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatusServer3On, "The cluster status result for a started node3 "
                                                                        "in the replicaset is not right")
        server2.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server2.status(self.env)

        expectedClusterStatusServer2On = [
        ('configReplSet0',['node1.test.com','node2.test.com','node3.test.com'], [
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_0',
                           log_file='/var/log/mongodb/node1_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node2_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_configReplSet0_0',
                           log_file='/var/log/mongodb/node2_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node3_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_configReplSet0_0',
                           log_file='/var/log/mongodb/node3_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None)])]

        clusterStatus = server2.getClusterStatus(server2.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatusServer2On, "The cluster status result for a started node2"
                                                                        " in the replicaset is not right")
        server1.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server1.status(self.env)

        expectedClusterStatusServer1On = [
        ('configReplSet0',['node1.test.com','node2.test.com','node3.test.com'], [
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node1_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_configReplSet0_0',
                           log_file='/var/log/mongodb/node1_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="PRIMARY"),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node2_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_configReplSet0_0',
                           log_file='/var/log/mongodb/node2_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY"),
            InstanceStatus(shard_name='configReplSet0',
                           pid_file_name='/var/run/mongodb/node3_configReplSet0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_configReplSet0_0',
                           log_file='/var/log/mongodb/node3_configReplSet0_0.log',
                           db_port='27019',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY")])]

        clusterStatus = server1.getClusterStatus(server1.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatusServer1On, "The cluster status result for a started node1"
                                                                        " in the replicaset is not right")

        server2.stop(self.env)
        with self.assertRaises(ComponentIsNotRunning):
            server2.status(self.env)

        server1.stop(self.env)
        with self.assertRaises(ComponentIsNotRunning):
            server1.status(self.env)

        server3.stop(self.env)
        with self.assertRaises(ComponentIsNotRunning):
            server3.status(self.env)


        clusterStatus = server3.getClusterStatus(server3.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_for_several_hosts_stopped,
                         "The cluster status result after stopping the replicaset is not right")
