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
#from mongos import MongosServer
#from mongo_base import InstanceConfig
#from mongo_base import InstanceStatus
from mongo_client import MongoClient

class UnitClientTest(IntegratedBaseTestCase):

    def cleanup(self):
        params.mongos_cluster_definition = ''
        params.mongod_cluster_definition = ''
        params.mongoconf_cluster_definition = ''

    def test_configure_mongo_client_for_sharding_cluster(self):
        self.cleanup()
        Script.config = {'clusterHostInfo': {
            'mongos_hosts': ['node1.test.com','node2.test.com'],
            'mongodb_hosts': ['node1.test.com'],
            'mongodc_hosts': []
        }}

        # Test without_mongos cluster definition
        client = MongoClient()
        client.configureMongoClient()
        self.assertEqual(params.mongos_hosts,'node1.test.com:27017,node2.test.com:27017',
                         'The mongos_hosts configuration is not right.')

        # Test with mongos cluster definition
        params.mongos_cluster_definition = 'node2.test.com,node1.test.com,node2.test.com'
        client.configureMongoClient()
        self.assertEqual(params.mongos_hosts, 'node2.test.com:27017,node1.test.com:27017,node2.test.com:27018',
                         'The mongos_hosts configuration is not right.')


    def test_configure_mongo_client_for_standalone(self):
        self.cleanup()
        Script.config = {'clusterHostInfo': {
            'mongos_hosts': [],
            'mongodb_hosts': ['node1.test.com'],
            'mongodc_hosts': []
        }}

        client = MongoClient()
        client.configureMongoClient()
        self.assertEqual(params.mongos_hosts, 'node1.test.com:27025',
                         'The mongos_hosts configuration is not right.')

    def test_configure_mongo_client_for_replicaset(self):
        self.cleanup()
        Script.config = {'clusterHostInfo': {
            'mongos_hosts': [],
            'mongodb_hosts': ['node1.test.com','node2.test.com'],
            'mongodc_hosts': []
        }}

        client = MongoClient()
        client.configureMongoClient()
        self.assertEqual(params.mongos_hosts, 'node1.test.com:27025',
                         'The mongos_hosts configuration is not right.')

        params.mongod_cluster_definition = 'node2.test.com,node1.test.com'

        client = MongoClient()
        client.configureMongoClient()
        self.assertEqual(params.mongos_hosts, 'node2.test.com:27025',
                         'The mongos_hosts configuration is not right.')

    # Integrated tests suggestions (Or mock for a given set of params?)
    def test_install_client(self):
        # Test if the sh file is installed
        pass

    def test_configure_for_sharding_cluster(self):
        pass

    def test_configure_for_standalone_mode(self):
        pass

    def test_configure_for_replicaset_mode(self):
        # Test if it will return the first if its stopped
        # Test if it will find the primary after started
        # Kill the primary and test if it will find the new primary is choosen
        pass
