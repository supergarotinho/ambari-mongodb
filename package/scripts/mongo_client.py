from resource_management import *

from mongo_base import MongoBase
import params

class MongoClient(MongoBase):
    client_config_path="/etc/mongoclient.conf"
    mongo_packages=['mongodb-org-shell', 'mongodb-org-tools']

    def install(self, env):
        env.set_params(params)
        self.installMongo(env)
        self.configure(env)
        File('/usr/local/bin/mongok',
             content=Template("mongok"),
             mode=0755
             )

    def configure(self,env):
        self.configureMongo(env)
        env.set_params(params)
        File(self.client_config_path,
             content=Template("mongoclient.conf.j2"),
             mode=0644
             )

    def configureMongo(self, env):
        """
            Configure the params needed to create the config template
        """
        pass

    def getPorts(self):
        """
        :rtype list[str]
        :return: The port list for this instance type
        """
        return self.parsePortsConfig(params.mongos_ports)


    def getClusterDefinition(self):
        """
        :rtype str
        :return: The cluster architecture configuration string
        """
        return params.mongos_cluster_definition


    def getShardPrefix(self):
        """
        :rtype str
        :return: The shard prefix configuration for this instance type
        """
        return ''


    def getHostsInAmbari(self):
        """
        Returns the ambari hosts for this instance

        :rtype  list[str]
        :return: Hosts list in ambari for this instance
        """
        config = Script.get_config()
        hosts_in_ambari = config['clusterHostInfo']['mongodb_hosts']  ## Service hosts list
        return hosts_in_ambari


    def getStartServerCommand(self, node):
        """
        :type node: InstanceConfig
        :rtype str
        :return: The command to start the given node for the given instance type
        """
        pass


    def startServer(self, node):
        """
        :type node: InstanceConfig
        :return: None
        """
        pass


    def startShardConfig(self, primary_node, nodes_to_add):
        """
        :type primary_node: InstanceStatus
        :type nodes_to_add: list[InstanceStatus]
        :rtype bool
        :param primary_node:
        :param nodes_to_add:
        :return: True if operation succeed, False otherwise
        """
        return True


    def addShardToMongos(self, shard_name, shard_hosts):
        """
         1. Check if there are mongos instances in ambari server
         2. Add this shard if all :
            * It is not already added
            * One of the mongos instances are on

        :type shard_name: str
        :type shard_hosts: list[InstanceStatus]
        :rtype bool
        :return: True if the shard is now in the mongos shard list
        """
        pass


    def setupCluster(self, service_list):
        """
        Setup the replicaset and shards conecting with each other

        :param service_list: list(tuple(str,list(str),list(InstanceConfig))]
        :param cluster_status: list(tuple(str,list(str),list(InstanceStatus))]
        :rtype None
        :return: None
        """
        pass

    def start(self, env, upgrade_type=None):
        """
        To be overridden by subclasses
        """
        pass

    def stop(self, env, upgrade_type=None):
        """
        To be overridden by subclasses
        """
        pass

    def status(self, env):
        pass

if __name__ == "__main__":
    MongoClient().execute()
