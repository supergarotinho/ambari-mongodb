import os
import sys
from time import sleep

# Ambari includes
from resource_management.core.exceptions import ComponentIsNotRunning
from resource_management.libraries.script import Script

# Custom service test classes includes
from integrated_base_test import IntegratedBaseTestCase

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(SCRIPT_DIR, '../package/scripts/')
SERVICE_DIR = os.path.join(SCRIPT_DIR, '../')
sys.path.append(PACKAGE_DIR)
sys.path.append(SERVICE_DIR)

# Custom service scripts includes
import params
from mongo_db import MongoDBServer
from mongo_base import InstanceConfig
from mongo_base import InstanceStatus
from mongo_config import MongoConfigServer
from mongos import MongosServer

class IntegratedShardedClusterTestCase(IntegratedBaseTestCase):

    def setUp(self):
        self.as_super = super(IntegratedShardedClusterTestCase, self)
        self.as_super.setUp()
        self.config_server = None
        self.mongos_server = None
        params.try_interval = 4
        params.times_to_try = 2

    def tearDown(self):
        self.as_super = super(IntegratedShardedClusterTestCase, self)
        self.as_super.tearDown()
        if self.config_server:
            self.config_server.stop(self.env)
        if self.mongos_server:
            self.mongos_server.stop(self.env)

    def cluster_setup(self):
        Script.config = {'clusterHostInfo': {
            'mongos_hosts': ['node1.test.com'],
            'mongodb_hosts': ['node1.test.com','node2.test.com','node3.test.com'],
            'mongodc_hosts': ['node1.test.com']
        }}

        params.mongod_cluster_definition = 'node1.test.com,node2.test.com/arbiter,node3.test.com,node2.test.com;' \
                                           'node2.test.com,node2.test.com,node3.test.com/arbiter'

        # Starting the required config server
        params.my_hostname = 'node1.test.com'
        self.config_server = MongoConfigServer()
        self.config_server.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        # Starting the mongos server
        self.mongos_server = MongosServer()
        self.mongos_server.start(self.env)

    expected_cluster_status_stopped = [
        ('shard0',['node1.test.com','node2.test.com/arbiter','node3.test.com','node2.test.com'], [
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node1_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_shard0_0',
                           log_file='/var/log/mongodb/node1_shard0_0.log',
                           db_port='27025',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_0',
                           log_file='/var/log/mongodb/node2_shard0_0.log',
                           db_port='27025',
                           host_name='node2.test.com',
                           is_arbiter=True,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node3_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_shard0_0',
                           log_file='/var/log/mongodb/node3_shard0_0.log',
                           db_port='27025',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_1.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_1',
                           log_file='/var/log/mongodb/node2_shard0_1.log',
                           db_port='27030',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None)]),
        ('shard1', ['node2.test.com', 'node2.test.com', 'node3.test.com/arbiter'], [
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node2_shard1_2.pid',
                           final_db_path='/var/lib/mongodb/node2_shard1_2',
                           log_file='/var/log/mongodb/node2_shard1_2.log',
                           db_port='27031',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node2_shard1_3.pid',
                           final_db_path='/var/lib/mongodb/node2_shard1_3',
                           log_file='/var/log/mongodb/node2_shard1_3.log',
                           db_port='27032',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node3_shard1_1.pid',
                           final_db_path='/var/lib/mongodb/node3_shard1_1',
                           log_file='/var/log/mongodb/node3_shard1_1.log',
                           db_port='27030',
                           host_name='node3.test.com',
                           is_arbiter=True,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None)])
    ]

    def test_sharded_cluster(self):
        self.cluster_setup()

        params.my_hostname = 'node3.test.com'
        server3 = MongoDBServer()
        params.my_hostname = 'node2.test.com'
        server2 = MongoDBServer()
        params.my_hostname = 'node1.test.com'
        server1 = MongoDBServer()

        clusterStatus = server3.getClusterStatus(server3.getClusterData())
        self.assertEqual(clusterStatus, self.expected_cluster_status_stopped,
                         "The cluster status result before stating the replicaset is not right")

        mongos_status, shard_list = server3.getMongosStatus('node1.test.com:27017')
        self.assertTrue(mongos_status,"Mongos MUST be running to execute this test!")
        self.assertEqual(len(shard_list),0,'The mongos must not know any shard at this first point!')

        server3.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server3.status(self.env)

        mongos_status, shard_list = server3.getMongosStatus('node1.test.com:27017')
        self.assertTrue(mongos_status,"Mongos MUST be running to execute this test!")
        self.assertEqual(len(shard_list),0,'The mongos must not know any shard at this second point!')

        expectedClusterStatusServer3On = [
        ('shard0',['node1.test.com','node2.test.com/arbiter','node3.test.com','node2.test.com'], [
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node1_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_shard0_0',
                           log_file='/var/log/mongodb/node1_shard0_0.log',
                           db_port='27025',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_0',
                           log_file='/var/log/mongodb/node2_shard0_0.log',
                           db_port='27025',
                           host_name='node2.test.com',
                           is_arbiter=True,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node3_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_shard0_0',
                           log_file='/var/log/mongodb/node3_shard0_0.log',
                           db_port='27025',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_1.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_1',
                           log_file='/var/log/mongodb/node2_shard0_1.log',
                           db_port='27030',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None)]),
        ('shard1', ['node2.test.com', 'node2.test.com', 'node3.test.com/arbiter'], [
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node2_shard1_2.pid',
                           final_db_path='/var/lib/mongodb/node2_shard1_2',
                           log_file='/var/log/mongodb/node2_shard1_2.log',
                           db_port='27031',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node2_shard1_3.pid',
                           final_db_path='/var/lib/mongodb/node2_shard1_3',
                           log_file='/var/log/mongodb/node2_shard1_3.log',
                           db_port='27032',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node3_shard1_1.pid',
                           final_db_path='/var/lib/mongodb/node3_shard1_1',
                           log_file='/var/log/mongodb/node3_shard1_1.log',
                           db_port='27030',
                           host_name='node3.test.com',
                           is_arbiter=True,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None)])
        ]

        clusterStatus = server3.getClusterStatus(server3.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatusServer3On, "The cluster status result for a started node3 "
                                                                        "in the replicaset is not right")
        server2.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server2.status(self.env)

        mongos_status, shard_list = server3.getMongosStatus('node1.test.com:27017')
        self.assertTrue(mongos_status,"Mongos MUST be running to execute this test!")
        self.assertEqual(len(shard_list),1,'The mongos must know one shard at this point!')

        expectedClusterStatusServer2On = [
        ('shard0',['node1.test.com','node2.test.com/arbiter','node3.test.com','node2.test.com'], [
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node1_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_shard0_0',
                           log_file='/var/log/mongodb/node1_shard0_0.log',
                           db_port='27025',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=False,
                           is_repl_configurated=None,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_0',
                           log_file='/var/log/mongodb/node2_shard0_0.log',
                           db_port='27025',
                           host_name='node2.test.com',
                           is_arbiter=True,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node3_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_shard0_0',
                           log_file='/var/log/mongodb/node3_shard0_0.log',
                           db_port='27025',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_1.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_1',
                           log_file='/var/log/mongodb/node2_shard0_1.log',
                           db_port='27030',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=False,
                           repl_role=None)]),
        ('shard1', ['node2.test.com', 'node2.test.com', 'node3.test.com/arbiter'], [
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node2_shard1_2.pid',
                           final_db_path='/var/lib/mongodb/node2_shard1_2',
                           log_file='/var/log/mongodb/node2_shard1_2.log',
                           db_port='27031',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="PRIMARY"),
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node2_shard1_3.pid',
                           final_db_path='/var/lib/mongodb/node2_shard1_3',
                           log_file='/var/log/mongodb/node2_shard1_3.log',
                           db_port='27032',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY"),
            InstanceStatus(shard_name='shard1',
                           pid_file_name='/var/run/mongodb/node3_shard1_1.pid',
                           final_db_path='/var/lib/mongodb/node3_shard1_1',
                           log_file='/var/log/mongodb/node3_shard1_1.log',
                           db_port='27030',
                           host_name='node3.test.com',
                           is_arbiter=True,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY")])
        ]

        clusterStatus = server2.getClusterStatus(server2.getClusterData())
        self.assertEqual(clusterStatus, expectedClusterStatusServer2On, "The cluster status result for a started node2"
                                                                        " in the replicaset is not right")
        server1.start(self.env)
        sleep(self.SLEEP_INTERVAL_AFTER_START_A_INSTANCE)
        server1.status(self.env)

        mongos_status, shard_list = server3.getMongosStatus('node1.test.com:27017')
        self.assertTrue(mongos_status,"Mongos MUST be running to execute this test!")
        self.assertEqual(len(shard_list),2,'The mongos must know two shards at this point!')

        expectedClusterStatusServer1On = [
        ('shard0',['node1.test.com','node2.test.com/arbiter','node3.test.com','node2.test.com'], [
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node1_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node1_shard0_0',
                           log_file='/var/log/mongodb/node1_shard0_0.log',
                           db_port='27025',
                           host_name='node1.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="PRIMARY"),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_0',
                           log_file='/var/log/mongodb/node2_shard0_0.log',
                           db_port='27025',
                           host_name='node2.test.com',
                           is_arbiter=True,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY"),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node3_shard0_0.pid',
                           final_db_path='/var/lib/mongodb/node3_shard0_0',
                           log_file='/var/log/mongodb/node3_shard0_0.log',
                           db_port='27025',
                           host_name='node3.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY"),
            InstanceStatus(shard_name='shard0',
                           pid_file_name='/var/run/mongodb/node2_shard0_1.pid',
                           final_db_path='/var/lib/mongodb/node2_shard0_1',
                           log_file='/var/log/mongodb/node2_shard0_1.log',
                           db_port='27030',
                           host_name='node2.test.com',
                           is_arbiter=False,
                           is_started=True,
                           is_repl_configurated=True,
                           repl_role="SECONDARY")]),
            ('shard1', ['node2.test.com', 'node2.test.com', 'node3.test.com/arbiter'], [
                InstanceStatus(shard_name='shard1',
                               pid_file_name='/var/run/mongodb/node2_shard1_2.pid',
                               final_db_path='/var/lib/mongodb/node2_shard1_2',
                               log_file='/var/log/mongodb/node2_shard1_2.log',
                               db_port='27031',
                               host_name='node2.test.com',
                               is_arbiter=False,
                               is_started=True,
                               is_repl_configurated=True,
                               repl_role="PRIMARY"),
                InstanceStatus(shard_name='shard1',
                               pid_file_name='/var/run/mongodb/node2_shard1_3.pid',
                               final_db_path='/var/lib/mongodb/node2_shard1_3',
                               log_file='/var/log/mongodb/node2_shard1_3.log',
                               db_port='27032',
                               host_name='node2.test.com',
                               is_arbiter=False,
                               is_started=True,
                               is_repl_configurated=True,
                               repl_role="SECONDARY"),
                InstanceStatus(shard_name='shard1',
                               pid_file_name='/var/run/mongodb/node3_shard1_1.pid',
                               final_db_path='/var/lib/mongodb/node3_shard1_1',
                               log_file='/var/log/mongodb/node3_shard1_1.log',
                               db_port='27030',
                               host_name='node3.test.com',
                               is_arbiter=True,
                               is_started=True,
                               is_repl_configurated=True,
                               repl_role="SECONDARY")])
        ]

        clusterStatus = server2.getClusterStatus(server2.getClusterData())
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
        self.assertEqual(clusterStatus, self.expected_cluster_status_stopped,
                         "The cluster status result after stopping the replicaset is not right")
