import os
import sys

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
from mongo_db import MongoDBServer

class IntegratedStandaloneMongodTestCase(IntegratedBaseTestCase):

    def setUp(self):
        self.as_super = super(IntegratedStandaloneMongodTestCase, self)
        self.as_super.setUp()
        Script.config['clusterHostInfo'] = {
            'mongos_hosts': [],
            'mongodb_hosts': ['node1.test.com'],
            'mongodc_hosts': []
        }
        params.times_to_try = 0

        # Configuring and Installing mongo config dependencies
        server = MongoDBServer()
        server.my_hostname = 'node1.test.com'
        server.configure(self.env)
        server.install(self.env)

    def test_start_status_stop_mongod(self):
        server = MongoDBServer()
        server.my_hostname = 'node1.test.com'

        with self.assertRaises(ComponentIsNotRunning):
            server.status(self.env)

        server.start(self.env)
        server.status(self.env)
        server.stop(self.env)

        with self.assertRaises(ComponentIsNotRunning):
            server.status(self.env)



