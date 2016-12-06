#!/usr/bin/env ambari-python-wrap
import re

"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
The naming convention for ServiceAdvisor subclasses depends on whether they are
in common-services or are part of the stack version's services.
In common-services, the naming convention is <service_name><service_version>ServiceAdvisor.
In the stack, the naming convention is <stack_name><stack_version><service_name>ServiceAdvisor.
Unlike the StackAdvisor, the ServiceAdvisor does NOT provide any inheritance.
If you want to use inheritance to augment a previous version of a service's
advisor you can use the following code to dynamically load the previous advisor.
Some changes will be need to provide the correct path and class names.
"""
import os
import imp
import traceback

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.join(SCRIPT_DIR, '../../../../../stacks/')
PARENT_FILE = os.path.join(PARENT_DIR, 'service_advisor.py')

try:
    with open(PARENT_FILE, 'rb') as fp:
        service_advisor = imp.load_module('service_advisor', fp, PARENT_FILE, ('.py', 'rb', imp.PY_SOURCE))
except Exception as e:
    traceback.print_exc()
    print "Failed to load parent"

from stack_advisor import DefaultStackAdvisor
from resource_management.core.logger import Logger
from collections import namedtuple

ShardNumbers = namedtuple('ShardNumbers', 'numberOfInstances numberOfArbiters')

# HDP23StackAdvisor
# DefaultStackAdvisor
# service_advisor.ServiceAdvisor

class HDP23MongoDBServiceAdvisor(DefaultStackAdvisor):
    """

    """

    MONGOS_COMPONENT_NAME = 'MONGOS'
    MONGODC_COMPONENT_NAME = 'MONGODC'
    MONGOD_COMPONENT_NAME = 'MONGODB'
    CLUSTER_DEFINITION_CONF_NAME = 'cluster_definition'
    PORTS_CONF_NAME = 'ports'

    def __init__(self, *args, **kwargs):
        Logger.initialize_logger()
        Logger.info("MongoDBServiceAdvisor has been created!")
        self.as_super = super(HDP23MongoDBServiceAdvisor, self)
        self.as_super.__init__(*args, **kwargs)

    """
    If any components of the service should be colocated with other services,
    this is where you should set up that layout.  Example:
      # colocate HAWQSEGMENT with DATANODE, if no hosts have been allocated for HAWQSEGMENT
      hawqSegment = [component for component in serviceComponents if component["StackServiceComponents"]["component_name"] == "HAWQSEGMENT"][0]
      if not self.isComponentHostsPopulated(hawqSegment):
        for hostName in hostsComponentsMap.keys():
          hostComponents = hostsComponentsMap[hostName]
          if {"name": "DATANODE"} in hostComponents and {"name": "HAWQSEGMENT"} not in hostComponents:
            hostsComponentsMap[hostName].append( { "name": "HAWQSEGMENT" } )
          if {"name": "DATANODE"} not in hostComponents and {"name": "HAWQSEGMENT"} in hostComponents:
            hostComponents.remove({"name": "HAWQSEGMENT"})
    """

    def colocateService(self, hostsComponentsMap, serviceComponents):
        pass

    """
    Any configuration recommendations for the service should be defined in this function.
    This should be similar to any of the recommendXXXXConfigurations functions in the stack_advisor.py
    such as recommendYARNConfigurations().
    """

    def getServiceConfigurationRecommendations(self, configurations, clusterSummary, services, hosts):
        return []

    """
    Returns an array of Validation objects about issues with the hostnames to which components are assigned.
    This should detect validation issues which are different than those the stack_advisor.py detects.
    The default validations are in stack_advisor.py getComponentLayoutValidations function.
    """

    def getServiceComponentLayoutValidations(self, services, hosts):
        Logger.info("Initiating MongoDB layout validation ...")

        componentsListList = [service["components"] for service in services["services"]]
        componentsList = [item["StackServiceComponents"] for sublist in componentsListList for item in sublist]

        mongodHosts = self.getHosts(componentsList, self.MONGOD_COMPONENT_NAME)
        mongoConfHosts = self.getHosts(componentsList, self.MONGODC_COMPONENT_NAME)
        mongosHosts = self.getHosts(componentsList, self.MONGOS_COMPONENT_NAME)

        Logger.info("Mongod hosts: "+str(mongodHosts))
        Logger.info("MongoConf hosts: "+str(mongoConfHosts))
        Logger.info("Mongos hosts: "+str(mongosHosts))

        items = []

        if (len(mongosHosts) > 0) and (len(mongoConfHosts) == 0):
            message = "For a sharding cluster, it must have Mongo Config Instances"
            items.append({"type": 'host-component', "level": 'ERROR', "message": message,
                          "component-name": self.MONGODC_COMPONENT_NAME})

        if (len(mongoConfHosts) > 0) and (len(mongosHosts) == 0):
            message = "For a sharding cluster, it must have one or more Mongos Query Router services"
            items.append({"type": 'host-component', "level": 'ERROR', "message": message,
                          "component-name": self.MONGOS_COMPONENT_NAME})

        return items

    def validateIfRootDir(self, properties, validationItems, prop_name, display_name):
        root_dir = '/'
        if prop_name in properties and properties[prop_name].strip() == root_dir:
            validationItems.append({"config-name": prop_name,
                                    "item": self.getWarnItem(
                                        "It is not advisable to have " + display_name + " at " + root_dir + ". Consider "
                                                                                                            "creating a sub directory for it")})

    def checkForMultipleDirs(self, properties, validationItems, prop_name, display_name):
        # check for delimiters space, comma, colon and semi-colon
        if prop_name in properties and len(re.sub(r'[,;:]', ' ', properties[prop_name]).split(' ')) > 1:
            validationItems.append({"config-name": prop_name,
                                    "item": self.getErrorItem(
                                        "Multiple directories for " + display_name + " are not allowed.")})

    def parsePortsConfig(self, ports_string):
        """
        Parse the user ports configuration

        :param ports_string: The ports configuration string
        :type ports_string: str
        :return: A list of ports
        :rtype list[str]
        """
        ports_string_list = ports_string.split(",")
        ports = []
        for spec in ports_string_list:
            if spec.find("-") > -1:
                limits = spec.split("-")
                for i in range(int(limits[0]), int(limits[1]) + 1):
                    ports.append(str(i))
            else:
                ports.append(spec)
        return ports

    def validatePortConfig(self, properties, validationItems, prop_name):
        """
            Check if the specified in the correct format
        """
        if prop_name in properties:
            ports = self.parsePortsConfig(properties[prop_name])
            for port in ports:
                try:
                    port_str = int(port)
                except:
                    validationItems.append({"config-name": prop_name,
                                            "item": self.getErrorItem(
                                                "The ports configuration is not valid. Please follow the recommended "
                                                "format.")})
                    break

    def checkForInexistentNodes(self, properties, validationItems, prop_name, ambari_hosts, component_display_name):
        Logger.info("Checking for inexistent nodes on " + component_display_name)
        Logger.info("Configuration name: " + prop_name)

        if prop_name in properties:
            cluster_definition = properties[prop_name]
            Logger.info("Cluster definition: " + cluster_definition)
            if len(cluster_definition.strip()) > 0:
                nodes_instances = {}
                cluster_shards = cluster_definition.split(";")
                for shard in cluster_shards:
                    shard_nodes = shard.split(",")
                    for node in shard_nodes:
                        if node.find("/arbiter") > -1:
                            node_name = node[0:node.find("/arbiter")]
                        else:
                            node_name = node

                        if node_name not in ambari_hosts:
                            validationItems.append({"config-name": prop_name,
                                                    "item": self.getErrorItem(
                                                        "The node " + node_name + " in the shard " + shard +
                                                        " does not have the " + component_display_name + " component "
                                                                                                         "Installed on Ambari. The Ambari nodes are: " +
                                                        str.join(",", ambari_hosts))})

                        # This will be used to check if some node does not have instances
                        if nodes_instances.has_key(node_name):
                            nodes_instances[node_name] += 1
                        else:
                            nodes_instances[node_name] = 1

                for node in ambari_hosts:
                    if not nodes_instances.has_key(node):
                        validationItems.append({"config-name": prop_name,
                                                "item": self.getWarnItem(
                                                    "The node " + node + " in ambari does not have any instances "
                                                                         "of " + component_display_name + " configured. You must remove the "
                                                                                                          "node in ambari install or add  some instances for it in the "
                                                                                                          "cluster configuration")})

    def getMinimumNumberOfPorts(self, cluster_definition):
        """
        Returns the minimum number of ports needed for a Node given the cluster definition

        :param cluster_definition: The config string for the cluster
        :type cluster_definition: str
        :return: int
        """
        nodes_ports = {}

        if len(cluster_definition.strip()) > 0:
            cluster_shards = cluster_definition.split(";")
            for shard in cluster_shards:
                shard_nodes = shard.split(",")
                for node in shard_nodes:
                    if node.find("/arbiter") > -1:
                        node_name = node[0:node.find("/arbiter")]
                    else:
                        node_name = node

                    if nodes_ports.has_key(node_name):
                        nodes_ports[node_name] += 1
                    else:
                        nodes_ports[node_name] = 1

        return max(nodes_ports.values())

    def validateMongoDBConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
        validationItems = []

        # 1. Check in some of directories are the root dir or with special chars
        directories = {
            'db_path': 'MongoDB DB Path Prefix',
            'log_path': 'MongoDB Log Path',
            'pid_db_path': 'MongoDB PID Path'
        }
        for property_name, display_name in directories.iteritems():
            self.validateIfRootDir(properties, validationItems, property_name, display_name)
            self.checkForMultipleDirs(properties, validationItems, property_name, display_name)

        return validationItems

    def validateMinNumberOfPorts(self, properties, validationItems, prop_name, cluster_definition,
                                 component_display_name):
        min_ports = self.getMinimumNumberOfPorts(cluster_definition)
        supplied_ports = len((self.parsePortsConfig(properties[prop_name])))
        if min_ports < supplied_ports:
            validationItems.append({"config-name": prop_name,
                                    "item": self.getErrorItem(
                                        "As your cluster has more than one instance of " + component_display_name +
                                        " per node, you need to supply more ports. You have supplied "
                                        + str(supplied_ports) + " ports. But there is an instance that requires "
                                        + str(min_ports) + " ports.")})

    def getClusterNumbers(self, cluster_definition):
        """

        :param cluster_definition:  The config string for the cluster
        :type cluster_definition: str
        :return: Cluster numbers for each shard
        :rtype: list[ShardNumbers]
        """
        shards = []

        if len(cluster_definition.strip()) > 0:
            cluster_shards = cluster_definition.split(";")
            for shard in cluster_shards:
                shard_nodes = shard.split(",")
                numberOfInstances = len(shard_nodes)
                numberOfArbiters = len(filter(lambda node: node.find("/arbiter") > -1, shard_nodes))
                shards.append(ShardNumbers(numberOfInstances, numberOfArbiters))

        return shards

    def validateMongoDInstancesConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
        mongod_configs = properties
        validationItems = []

        componentsListList = [service["components"] for service in services["services"]]
        componentsList = [item["StackServiceComponents"] for sublist in componentsListList for item in sublist]

        mongodHosts = self.getHosts(componentsList, self.MONGOD_COMPONENT_NAME)

        # 1. Check if all nodes in the cluster_configuration has the component installed on ambari
        self.checkForInexistentNodes(properties, validationItems, self.CLUSTER_DEFINITION_CONF_NAME, mongodHosts,
                                     "Mongo DB Server")

        # 2. Check the port configurations
        self.validatePortConfig(properties, validationItems, self.PORTS_CONF_NAME)

        # 3. Check if we have met the minimum number of needed ports
        self.validateMinNumberOfPorts(properties, validationItems, self.PORTS_CONF_NAME,
                                      mongod_configs[self.CLUSTER_DEFINITION_CONF_NAME], "Mongo DB Server")

        # 4. Check if we have more than one arbiter per shard
        shardsNumbers = self.getClusterNumbers(mongod_configs[self.CLUSTER_DEFINITION_CONF_NAME])
        if len(filter(lambda shard: shard.numberOfArbiters > 1, shardsNumbers)) > 0:
            validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                    "item": self.getWarnItem(
                                        "It is not advisable to have more than one arbiter per shard. Consider "
                                        "changing the cluster configuration.")})

        # 5. Check if we have an arbiter as the first node of a shard
        cluster_shards = mongod_configs[self.CLUSTER_DEFINITION_CONF_NAME].split(";")
        for shard in cluster_shards:
            shard_nodes = shard.split(",")
            if shard_nodes[0].find("/arbiter") > -1:
                validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                        "item": self.getErrorItem(
                                            "The first node of the shard must not be an arbiter. You must change the "
                                            "position of the " + shard_nodes[0] + " in the shard " + shard)})

        return validationItems

    def validateMongoConfigInstancesConfigurations(self, properties, recommendedDefaults, configurations, services,
                                                   hosts):
        Logger.info("Initiating mongo-conf configuration validation...")

        mongoconf_configs = properties
        validationItems = []

        componentsListList = [service["components"] for service in services["services"]]
        componentsList = [item["StackServiceComponents"] for sublist in componentsListList for item in sublist]

        mongoConfHosts = self.getHosts(componentsList, self.MONGODC_COMPONENT_NAME)

        # 1. Check if all nodes in the cluster_configuration has the component installed on ambari
        # 1.1 It also check if some node in ambari does not have any instances
        self.checkForInexistentNodes(properties, validationItems, self.CLUSTER_DEFINITION_CONF_NAME, mongoConfHosts,
                                     "Mongo Config Server")

        # 2. Check the port configurations
        self.validatePortConfig(properties, validationItems, self.PORTS_CONF_NAME)

        # 3. Check if we have met the minimum number of needed ports
        self.validateMinNumberOfPorts(properties, validationItems, self.PORTS_CONF_NAME,
                                      mongoconf_configs[self.CLUSTER_DEFINITION_CONF_NAME], "Mongo Config Server")

        # 4. Check if we have just one shard
        shardsNumbers = self.getClusterNumbers(mongoconf_configs[self.CLUSTER_DEFINITION_CONF_NAME])
        if len(shardsNumbers) > 1:
            validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                    "item": self.getErrorItem(
                                        "You can't have more than one shard for mongo db config instances. You have "
                                        "configured " + str(len(shardsNumbers)) + " shards for it.")})

        # 5. Check if we have exactly 3 mongo config instances
        if len(shardsNumbers) == 1:
            if shardsNumbers[0].numberOfInstances != 3:
                validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                        "item": self.getErrorItem(
                                            "You must have 3 Mongo Config Instances. You have configured " +
                                            str(shardsNumbers[0].numberOfInstances) + " instances for it.")})
        elif len(shardsNumbers) == 0:
            if len(mongoConfHosts) < 3:
                validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                        "item": self.getErrorItem(
                                            "You must have 3 Mongo Config Instances. As you have only " +
                                            str(len(mongoConfHosts)) + " nodes available for Mongo Config Instances. "
                                                                       "You have two options. 1-Change the cluster definition property in "
                                                                       "mongo-conf configuration specifying more instances per node in order to "
                                                                       "archieve 3 mongo config instances. 2-Add more nodes with mongo config in "
                                                                       "ambari.")})

        # 6. Check if we have any arbiters (mongoconf does not support arbiters)
        if len(filter(lambda shard: shard.numberOfArbiters > 0, shardsNumbers)) > 0:
            validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                    "item": self.getErrorItem(
                                        "You can't have any arbiters in mongo config replicaset.")})

        return validationItems

    def validateMongoSInstancesConfigurations(self, properties, recommendedDefaults, configurations, services, hosts):
        mongos_configs = properties
        validationItems = []

        componentsListList = [service["components"] for service in services["services"]]
        componentsList = [item["StackServiceComponents"] for sublist in componentsListList for item in sublist]

        mongoConfHosts = self.getHosts(componentsList, self.MONGODC_COMPONENT_NAME)

        # 1. Check if all nodes in the cluster_configuration has the component installed on ambari
        # 1.1 It also check if some node in ambari does not have any instances
        self.checkForInexistentNodes(properties, validationItems, self.CLUSTER_DEFINITION_CONF_NAME, mongoConfHosts,
                                     "Mongo Query Router")

        # 2. Check the port configurations
        self.validatePortConfig(properties, validationItems, self.PORTS_CONF_NAME)

        # 3. Check if we have met the minimum number of needed ports
        self.validateMinNumberOfPorts(properties, validationItems, self.PORTS_CONF_NAME,
                                      mongos_configs[self.CLUSTER_DEFINITION_CONF_NAME], "Mongo Query Router")

        # 4. Check if we have just one shard
        shardsNumbers = self.getClusterNumbers(mongos_configs[self.CLUSTER_DEFINITION_CONF_NAME])
        if len(shardsNumbers) > 1:
            validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                    "item": self.getErrorItem(
                                        "You can't have more than one shard for Mongo Query Router instances. You have "
                                        "configured " + str(len(shardsNumbers)) + " shards for it.")})

        # 5. Check if we have any arbiters (mongoconf does not support arbiters)
        if len(filter(lambda shard: shard.numberOfArbiters > 0, shardsNumbers)) > 0:
            validationItems.append({"config-name": self.CLUSTER_DEFINITION_CONF_NAME,
                                    "item": self.getErrorItem(
                                        "You can't have any arbiters in Mongo Query Router configuration.")})

        return validationItems

    """
    Any configuration validations for the service should be defined in this function.
    This should be similar to any of the validateXXXXConfigurations functions in the stack_advisor.py
    such as validateHDFSConfigurations.
    """

    def getServiceConfigurationsValidationItems(self, configurations, recommendedDefaults, services, hosts):
        Logger.info("Initiating MongoDb Configuration Check!")

        siteName = "mongodb"
        method = self.validateMongoDBConfigurations
        items = self.validateConfigurationsForSite(configurations, recommendedDefaults, services, hosts, siteName,
                                                   method)

        siteName = "mongod"
        method = self.validateMongoDInstancesConfigurations
        resultItems = self.validateConfigurationsForSite(configurations, recommendedDefaults, services, hosts, siteName,
                                                         method)
        items.extend(resultItems)

        siteName = "mongo-config"
        method = self.validateMongoConfigInstancesConfigurations
        resultItems = self.validateConfigurationsForSite(configurations, recommendedDefaults, services, hosts, siteName,
                                                         method)
        items.extend(resultItems)

        siteName = "mongos"
        method = self.validateMongoSInstancesConfigurations
        resultItems = self.validateConfigurationsForSite(configurations, recommendedDefaults, services, hosts, siteName,
                                                         method)
        items.extend(resultItems)

        return items
