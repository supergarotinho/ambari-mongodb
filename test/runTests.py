#!/usr/bin/env python

import sys
import os
from resource_management.core.environment import Environment
from resource_management.libraries.script import Script
from resource_management.core.logger import Logger

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PACKAGE_DIR = os.path.join(SCRIPT_DIR, '../package/scripts/')
SERVICE_DIR = os.path.join(SCRIPT_DIR, '../')
sys.path.append(PACKAGE_DIR)
sys.path.append(SERVICE_DIR)

import params
from mongo_config import *
from mongo_db import *
from mongos import *
from mongo_client import *

if len(sys.argv) == 5 and (sys.argv[4] is 'simulate'):
    server_type = sys.argv[1]
    operation = sys.argv[2]
    server_name = sys.argv[3]

    env = Environment(SERVICE_DIR, tmp_dir=SERVICE_DIR)
    env.__enter__()

    ## Modifying os to add the names to the hosts
    os.system(os.path.join(SCRIPT_DIR,'set_tests_env.sh'))

    ## Setting up configurations
    Script.config = {'clusterHostInfo': {
        'mongos_hosts': ['node1.test.com',
                         'node2.test.com'],
        'mongodb_hosts': ['node1.test.com',
                         'node2.test.com',
                         'node3.test.com'],
        'mongodc_hosts': ['node1.test.com',
                         'node2.test.com',
                         'node3.test.com']
    }}


    Logger.info("Server type: " + server_type)
    Logger.info("Operation: " + operation)
    Logger.info("Server name: " + server_name)
    Logger.info("...")
    params.my_hostname = server_name

    if server_type == 'conf':
        server = MongoConfigServer()
    elif server_type == 'mongod':
        server = MongoDBServer()
    elif server_type == 'mongos':
        server = MongosServer()
    elif server_type == 'client':
        server = MongoClient()

    if operation == 'start':
        Logger.info('Starting the server...')
        server.start(env)
    elif operation == 'status':
        Logger.info('Checking the server status...')
        server.status(env)
    elif operation == 'stop':
        Logger.info('Stopping the server...')
        server.stop(env)
    elif operation == 'install':
        server.install(env)