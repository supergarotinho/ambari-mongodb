from resource_management.core.logger import Logger
from resource_management.core.resources.system import File
from resource_management.core.source import InlineTemplate
from resource_management.libraries.script import Script
from resource_management.libraries.functions.format import format
from time import sleep
import params
from mongo_base import InstanceConfig
from mongo_base import InstanceStatus
from mongo_startable import MongoStartable

class MongosServer(MongoStartable):
    def __init__(self):
        # self.hosts_in_ambari = "mandachuva.falometro.com.br,batatinha01.falometro.com.br,batatinha02.falometro.com.br".split(',')
        self.mongodb_config_file = '/etc/mongos.conf'

    def configureMongo(self, env):
        """
            Create the config file based on the user configuration
        """
        Logger.info("Configuring the file: " + self.mongodb_config_file)
        config_content = InlineTemplate(params.mongos_config_content)
        File(self.mongodb_config_file, content=config_content)

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
        hosts_in_ambari = config['clusterHostInfo']['mongodb_hosts']   ## Service hosts list
        return hosts_in_ambari

    def getConfigServerList(self):
        """

        :rtype list[str]
        :return: List of config servers in form of "host:port"
        """
        db_conf_ports = self.parsePortsConfig(params.mongoconf_ports)
        config = Script.get_config()
        ambari_mongoconfig_hosts = config['clusterHostInfo']['mongodc_hosts']   ## Service hosts list

        #ambari_mongoconfig_hosts = "mandachuva.falometro.com.br,batatinha01.falometro.com.br,batatinha02.falometro.com.br".split(
         #   ',')

        if len(params.mongoconf_cluster_definition.lstrip().rstrip()) > 0:
            mongod_cluster = params.mongoconf_cluster_definition.split(",")
        else:
            mongod_cluster = ambari_mongoconfig_hosts

        nodes_and_port_indexes = {}
        for host in ambari_mongoconfig_hosts:
            nodes_and_port_indexes[host] = 0

        mongo_config_servers = []

        for index_nodes, node_name in enumerate(mongod_cluster, start=0):
            Logger.info('Processing config server node #: ' + str(index_nodes))
            Logger.info('Config Server Name: ' + node_name)
            db_port = db_conf_ports[nodes_and_port_indexes[node_name]]
            Logger.info('Config Server db port:' + db_port)
            mongo_config_servers.append(node_name + ":" + db_port)

        return mongo_config_servers

    def getStartServerCommand(self,node):
        """
        :type node: InstanceConfig
        :rtype str
        :return: The command to start the given node for the given instance type
        """
        Logger.info("Starting a mongos instance in this machine...")
        pid_file_name = node.pid_file_name
        port = node.db_port
        log_file_name = node.log_file
        host_name = node.host_name

        mongo_config_servers = self.getConfigServerList()

        config_db_str = params.mongoconf_shard_prefix + '0/' + reduce(lambda x, y: x + ',' + y, mongo_config_servers)

        return format('sudo -u mongodb mongos --fork --bind_ip {host_name} '
                      ' --port {port} --configdb {config_db_str} '
                      ' --logappend --logpath {log_file_name} --pidfilepath {pid_file_name}')


    def startServer(self, node):
        """
        :type node: InstanceConfig
        :return: None
        """
        mongos_node = InstanceConfig(node.shard_name,
                                     node.pid_file_name,
                                     '',
                                     node.log_file,
                                     node.db_port,
                                     node.host_name,
                                     node.is_arbiter)
        super(MongosServer, self).startServer(mongos_node)


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


    def start(self, env):
        self.configure(env)
        Logger.info("Checking if the primary config server is alive ...")

        config_server_list = self.getConfigServerList()

        config_server_instances = []

        for server in  config_server_list:
            server_data = server.split(":")
            node_instance = InstanceConfig(params.mongoconf_shard_prefix + '0', '', '', '',
                                           server_data[1], server_data[0], False)
            config_server_instances.append(node_instance)

        config_cluster_shard_list = [(params.mongoconf_shard_prefix + '0',
                                      config_server_list,
                                      config_server_instances)]

        times_to_try = params.times_to_try
        try_interval = params.try_interval
        times = 0
        while times < times_to_try:
            config_cluster_status = self.getClusterStatus(config_cluster_shard_list)

            # Se tiver um config server ativo e primario, podemos continuar
            if len(filter(lambda node: (node.is_started is True) and
                                       (node.is_repl_configurated is True) and
                                       (node.repl_role == 'PRIMARY'),config_cluster_status[0][2])) > 0:
                Logger.info("There is a PRIMARY config server on! Lets start the mongos instances!")
                super(MongosServer, self).start(env)
                break
            else:
                Logger.info("None of the config server instances are on ...")
                Logger.info('Waiting ' + str(try_interval) + ' seconds for all instances starts....')
                sleep(try_interval)
                times += 1

if __name__ == "__main__":
    MongosServer().execute()
