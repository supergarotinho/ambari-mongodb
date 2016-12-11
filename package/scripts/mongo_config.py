import commands
import os
import logging
from resource_management import *
from collections import *
from mongo_base import *
from mongo_startable import MongoStartable

class MongoConfigServer(MongoStartable):

    def __init__(self, *args, **kwargs):
        self.as_super = super(MongoConfigServer, self)
        self.as_super.__init__(*args, **kwargs)
        self.mongodb_config_file = '/etc/mongoconfig.conf'

    def configureMongo(self, env):
        """
            Create the config file based on the user configuration
        """
        import params
        Logger.info("Configuring the file: " + self.mongoconf_config_file)
        config_content = InlineTemplate(params.mongoconf_config_content)
        File(self.mongoconf_config_file, content=config_content)

    def getPorts(self):
        """
        :rtyxpe list[str]
        :rexturn: The port list for this instance type
        """
        import params
        return self.parsePortsConfig(params.mongoconf_ports)

    def getClusterDefinition(self):
        """
        :rtype str
        :return: The cluster architecture configuration string
        """
        import params
        return params.mongoconf_cluster_definition

    def getShardPrefix(self):
        """
        :rtype str
        :return: The shard prefix configuration for this instance type
        """
        import params
        return params.mongoconf_shard_prefix

    def getHostsInAmbari(self):
        """
        Returns the ambari hosts for this instance

        :rtype  list[str]
        :return: Hosts list in ambari for this instance
        """
        config = Script.get_config()
        hosts_in_ambari = config['clusterHostInfo']['mongodc_hosts']   ## Service hosts list
        return hosts_in_ambari

    def getStartServerCommand(self,node):
        """
        :type node: InstanceConfig
        :rtype str
        :return: The command to start the given node for the given instance type
        """
        import params
        Logger.info("Starting a config server instance in this machine...")
        shard_name = node.shard_name
        pid_file_name = node.pid_file_name
        final_db_path = node.final_db_path
        port = node.db_port
        log_file_name = node.log_file
        host_name = node.host_name
        db_user = params.mongodb_user
        config_file = self.mongodb_config_file

        return format('sudo -u {db_user} mongod --configsvr --replSet {shard_name} --bind_ip {host_name} '
                      ' --port {port} --dbpath {final_db_path} --oplogSize 100 '
                      ' --fork --logappend --logpath {log_file_name} --pidfilepath {pid_file_name} --config {config_file}')

    def startShardConfig(self, primary_node, nodes_to_add):
        """
        :type primary_node: InstanceStatus
        :type nodes_to_add: list[InstanceStatus]
        :rtype bool
        :param primary_node:
        :param nodes_to_add:
        :return: True if operation succeed, False otherwise
        """
        Logger.info('Starting the configuration for shard: ' + primary_node.shard_name)
        server = primary_node.host_name + ':' + primary_node.db_port
        command_string = 'mongo ' + server + ' --eval \'rs.initiate({' + '_id: "' + primary_node.shard_name + \
                         '",configsvr: true,members: [' + '{ _id: 0, host: "' + server + '" }]})\''

        success_message = 'The replicaset was create with success!'
        error_message = 'The replicaset could not be created!'
        result = self.executeMongoCommand(command_string, success_message, error_message)

        if result:
            for node in nodes_to_add:
                self.addNodeToShard(primary_node, node)

        return result

    def addShardToMongos(self,shard_name,shard_hosts):
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
        return True


if __name__ == "__main__":
    MongoConfigServer().execute()