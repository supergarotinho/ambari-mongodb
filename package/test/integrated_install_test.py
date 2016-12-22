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

from mongo_db import MongoDBServer
from mongos import MongosServer
from mongo_config import MongoConfigServer

class IntegratedMongoConfTestCase(IntegratedBaseTestCase):

    def test_mongod_configure(self):
        server = MongoDBServer()
        server.my_hostname = 'node1.test.com'
        server.configure(self.env)

        self.assertTrue(os.path.exists(server.mongodb_config_file),"The config file for mongod instances does not exists")

    def test_mongod_install(self):
        server = MongoDBServer()
        server.my_hostname = 'node1.test.com'
        server.install(self.env)

    def test_mongoconf_configure(self):
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'
        server.configure(self.env)

        self.assertTrue(os.path.exists(server.mongodb_config_file), "The config file for mongoconf instances does not exists")

    def test_mongoconf_install(self):
        server = MongoConfigServer()
        server.my_hostname = 'node1.test.com'
        server.install(self.env)

    def test_mongos_configure(self):
        server = MongosServer()
        server.my_hostname = 'node1.test.com'
        server.configure(self.env)

        self.assertTrue(os.path.exists(server.mongodb_config_file), "The config file for mongos instances does not exists")

    def test_mongos_install(self):
        server = MongosServer()
        server.my_hostname = 'node1.test.com'
        server.install(self.env)
