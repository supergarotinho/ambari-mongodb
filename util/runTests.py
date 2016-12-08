#!/usr/bin/env python

import sys
import os
from resource_management.core.environment import Environment
from resource_management.libraries.script import Script
from resource_management.core.logger import Logger
# Threading support to isntantiate multiple services in paralel
from multiprocessing import Process

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

def configureHosts(hosts):
    """

    :type hosts: dict
    :param hosts: A dictionary with 'host_name': 'ip' values
    :return: None
    """
    for key, value in hosts.iteritems():
        command_str = 'echo "' + value + ' ' + key + '" >> /etc/hosts'
        Logger.info("Executing the following command: " + command_str)
        os.system(command_str)

def cleanHosts():
    """
    Clean the modifications made on /etc/hosts file for testing

    :return: None
    """
    command_str = "cat /etc/hosts | sed '/\.test\.com/D' > /tmp/hosts"
    Logger.info("Executing the following command: " + command_str)
    os.system(command_str)
    command_str = "cat /tmp/hosts > /etc/hosts"
    Logger.info("Executing the following command: " + command_str)
    os.system(command_str)


def getServerObject(server_type):
    if server_type == 'conf':
        return MongoConfigServer()
    elif server_type == 'mongod':
        return MongoDBServer()
    elif server_type == 'mongos':
        return MongosServer()

def startMongoInstances(server_type,hosts):
    Logger.info("Starting servers of type: " + server_type)
    process_list = []
    for server_name in hosts:
        Logger.info("Server name: " + server_name)
        params.my_hostname = server_name
        server = getServerObject(server_type)
        p = Process(target=server.start, args=(env,))
        process_list.append(p)
        p.start()
    for p in process_list:
        p.join()

def getMongoInstancesStatus(server_type,hosts):
    Logger.info("Starting servers of type: " + server_type)
    process_list = []
    for server_name in hosts:
        Logger.info("Server name: " + server_name)
        params.my_hostname = server_name
        server = getServerObject(server_type)
        p = Process(target=server.status, args=(env,))
        process_list.append(p)
        p.start()
    for p in process_list:
        p.join()

def stopMongoInstances(server_type,hosts):
    Logger.info("Starting servers of type: " + server_type)
    process_list = []
    for server_name in hosts:
        Logger.info("Server name: " + server_name)
        params.my_hostname = server_name
        server = getServerObject(server_type)
        p = Process(target=server.stop, args=(env,))
        process_list.append(p)
        p.start()
    for p in process_list:
        p.join()


env = Environment(SERVICE_DIR, tmp_dir=SERVICE_DIR)
env.__enter__()

if len(sys.argv) == 3:
    Logger.info("Initiating process...")

    hosts = {'node1.test.com': '127.69.0.1',
             'node2.test.com': '127.69.0.2',
             'node3.test.com': '127.69.0.3'}
    operation = sys.argv[1]
    instanceOp = sys.argv[2]
    if operation == 'install':
        Logger.info("Installing...")
        configureHosts(hosts)
    elif operation == 'remove':
        Logger.info("Removing...")
        cleanHosts()
    elif operation == 'simulate':
        Logger.info("Simulating...")
        ## Setting up Ambari servers
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
        params.mongod_cluster_definition = 'node1.test.com,node2.test.com,node3.test.com;' \
                                              'node1.test.com,node1.test.com/arbiter,node2.test.com;' \
                                              'node2.test.com,node3.test.com,node3.test.com/arbiter'
        params.mongos_cluster_definition = 'node1.test.com,node1.test.com,node2.test.com'

        if instanceOp == 'start':
            startMongoInstances('conf',hosts.keys())
            startMongoInstances('mongos',hosts.keys())
            startMongoInstances('mongod',hosts.keys())
        elif instanceOp == 'status':
            getMongoInstancesStatus('conf',hosts.keys())
            getMongoInstancesStatus('mongos',hosts.keys())
            getMongoInstancesStatus('mongod',hosts.keys())
        elif instanceOp == 'stop':
            stopMongoInstances('conf', hosts.keys())
            stopMongoInstances('mongos', hosts.keys())
            stopMongoInstances('mongod', hosts.keys())
else:
    Logger.info("Wrong usage. Argument length: "+ str(len(sys.argv)) + ". Arguments: " + str(sys.argv))

