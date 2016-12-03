import json
import commands
import os
import logging
import params
import ambari_simplejson as json # simplejson is much faster comparing to Python 2.6 json module and has the same functions set.
import params

from collections import *
from resource_management import *
from time import sleep

InstanceConfig = namedtuple('InstanceConfig','shard_name pid_file_name final_db_path log_file db_port host_name is_arbiter')
InstanceStatus = namedtuple('InstanceStatus', InstanceConfig._fields + ('is_started','is_repl_configurated','repl_role'))
Shard = namedtuple('ShardConfig','shard_name,shard_node_list,result_nodes')
Mongos = namedtuple('Mongos','pid_file_name log_file db_port host_name is_started')

class MongoBase(Script):
    repos_file_path = '/etc/yum.repos.d/mongodb.repo'
    mongoconf_config_file = '/etc/mongoconf.conf'
    mongos_config_file = '/etc/mongos.conf'
    mongo_packages = ['mongodb-org']

    def install(self, env):
        Logger.info('Installing mongo...')
        import params
        env.set_params(params)
        self.installMongo(env)

    def installMongo(self, env):
        self.install_packages(env)

        if os.path.exists(self.repos_file_path):
            Logger.info("File exists")
        else:
            Logger.info("File not exists")
            File(self.repos_file_path,
                 content=Template("mongodb.repo"),
                 mode=0644
                 )
        print "Installing mongodb..."
        if self.mongo_packages is not None and len(self.mongo_packages):
            for pack in self.mongo_packages:
                Package(pack)

    def configure(self, env):
        Logger.info('Configuring mongo...')
        import params
        env.set_params(params)
        self.configureMongo(env)

    def configureMongo(self, env):
        """
            To be overridden by subclasses
        """
        self.fail_with_error("configureMongo method isn't implemented")

    def parsePortsConfig(self,ports_string):
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

    def getPorts(self):
        """
        :rtype list[str]
        :return: The port list for this instance type
        """
        self.fail_with_error("getPorts method isn't implemented")

    def getClusterDefinition(self):
        """
        :rtype str
        :return: The cluster architecture configuration string
        """
        self.fail_with_error("getClusterDefinition method isn't implemented")

    def getShardPrefix(self):
        """
        :rtype str
        :return: The shard prefix configuration for this instance type
        """
        self.fail_with_error("getShardPrefix method isn't implemented")

    def getHostsInAmbari(self):
        """
        Returns the ambari hosts for this instance

        :rtype  list[str]
        :return: Hosts list in ambari for this instance
        """
        self.fail_with_error("getHostsInAmbari method isn't implemented")

    def getStartServerCommand(self,node):
        """
        :type node: InstanceConfig
        :rtype str
        :return: The command to start the given node for the given instance type
        """
        self.fail_with_error("getStartServerCommand method isn't implemented")

    def parseMongoResult(self,resultString):
        """

        :param resultString: the output string from the mongodb eval command
        :return: JSON parsed object
        """
        # Cleaning the mongo bson result and transforming in JSON before parsing it
        mongo_clean_begin_regex = re.compile('[^{]*{')
        mongo_line_break_regex = re.compile('\n')
        mongo_tabs_regex = re.compile('\t')
        resultClean = '[' + re.sub(r'NumberLong\s*\(\s*(\S+)\s*\)', r'\1',
                                   re.sub(r'ISODate\s*\(\s*(\S+)\s*\)', r'\1',
                                          re.sub(r'Timestamp\s*\(\s*(\S+), \S+\s*\)', r'\1',
                                                 mongo_tabs_regex.sub("",
                                                                      mongo_line_break_regex.sub(" ",
                                                                                                 mongo_clean_begin_regex.sub(
                                                                                                     '{', resultString,
                                                                                                     1)))))) + ']'
        return json.loads(resultClean)

    def executeMongoCommand(self, command_string, success_message, error_message):
        """
        Execute a mongodb eval command, parse the json results and print logs

        :param command_string: The command to be executed
        :param success_message: The success log message
        :param error_message: The error message
        :rtype bool
        :return: True if operation succeed, False otherwise
        """
        result = False
        Logger.info('Executing the following command: ' + command_string)
        cmd_result = commands.getstatusoutput(command_string)

        if cmd_result[0] == 0:
            Logger.info('Command executed without error. Parsing results...')
            mongo_result_json = self.parseMongoResult(cmd_result[1])
            mongoResultOk = str(mongo_result_json[0]['ok']).lstrip().rstrip()
            Logger.info('Command ok result:' + mongoResultOk)
            result = (mongoResultOk == '1')
            if result:
                Logger.info(success_message)
            else:
                error = str(mongo_result_json[0]['errmsg']).lstrip().rstrip()
                Logger.info(error_message + ' The resulting error: ' + error)
        else:
            Logger.info('Command exits with status code:' + str(cmd_result[0]))

        return result

    def addNodeToShard(self, primary_node, node):
        """
        :type primary_node: InstanceStatus
        :type node: InstanceStatus
        :rtype bool
        :param primary_node: The PRIMARY node of the shard
        :param node: The node to add to the shard
        :return: True if operation succeed, False otherwise
        """
        Logger.info('Adding node ' + node.host_name + ':' + node.db_port + ' to shard ' + primary_node.shard_name)
        server = primary_node.host_name + ':' + primary_node.db_port
        node_string = node.host_name + ':' + node.db_port
        command_string = 'mongo ' + server + ' --eval \'rs.add("' + node_string + '")\''

        success_message = 'The instance was added with success!'
        error_message = 'The instance could not be added!'
        return self.executeMongoCommand(command_string, success_message, error_message)


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
                         '",configsvr: false,members: [' + '{ _id: 0, host: "' + server + '" }]})\''

        success_message = 'The replicaset was create with success!'
        error_message = 'The replicaset could not be created!'
        result = self.executeMongoCommand(command_string, success_message, error_message)

        if result:
            for node in nodes_to_add:
                self.addNodeToShard(primary_node, node)

        return result

    def getMongosHostsInAmabari(self):
        """
        Returns the ambari hosts for this mongos instances

        :rtype  list[str]
        :return: Hosts list in ambari for mongos instance
        """
        # TODO: Mudar para a chamada correta
        """
        config = Script.get_config()
        hosts_in_ambari = config['clusterHostInfo']['mongodb_hosts']  ## Service hosts list
        """
        return "mandachuva.falometro.com.br,batatinha01.falometro.com.br".split(",")

    def getMongosStatus(self,mongos_server):
        """
        This method returns the status of the mongos instance and the shards the it knows

        :param mongos_server: the server location in the following format: "hostname:port"
        :return: tuple(bool,list[str])
        """
        command_string = "mongo " + mongos_server + " --eval 'sh.status()'"

        result_ok = False
        shard_list = []
        Logger.info('Executing the following command: ' + command_string)
        cmd_result = commands.getstatusoutput(command_string)

        if cmd_result[0] == 0:
            result_ok = True
            Logger.info('Command executed without error. Parsing results...')
            resulting_lines = map(lambda line: line.lstrip().rstrip(), cmd_result[1].split('\n'))
            shards = resulting_lines[resulting_lines.index('shards:') + 1:resulting_lines.index('active mongoses:')]
            Logger.info("Shard list in this mongos: " + str(shards))

            shards_json = json.loads('[' + reduce(lambda x, y: x + ',' + y, shards) + ']')
            for shard in shards_json:
                shard_list.append(shard["_id"])
        else:
            Logger.info("The mongos server is not on....")

        return (result_ok, shard_list)

    def getMongosList(self):
        """
        This method returns the data of all mongos instances in the cluster.
        This method is implemented here because it is need for most of the child classes.

        :type primary_node: InstanceStatus
        :type nodes_to_add: list[InstanceStatus]
        :rtype tuple(list[Mongos],list[str])
        :return: This method returns the data of all mongos instances in the cluster and the shards that they know of
        """
        Logger.info('Getting mongos cluster configuration...')
        cluster_config = params.mongos_cluster_definition
        db_ports = self.parsePortsConfig(params.mongos_ports)
        my_hostname = params.my_hostname
        mongos_hosts_in_ambari = self.getMongosHostsInAmabari()

        Logger.info('Mongos Cluster definition: ' + cluster_config)
        Logger.info('Database ports: ' + str(db_ports))
        Logger.info('My hostname: ' + my_hostname)
        Logger.info('Mongos Hosts in ambari: ' + str(mongos_hosts_in_ambari))
        Logger.info('PID path: ' + params.pid_db_path)
        Logger.info('Log path: ' + params.log_path)

        # prepare to cases where we do not have this config
        if cluster_config == '':
            Logger.info('Mongos hosts with uma instance per host: ' + str(mongos_hosts_in_ambari))
            cluster_config = reduce(lambda a, b: a + ',' + b, mongos_hosts_in_ambari)

        node_list = cluster_config.split(',')
        Logger.info('Number of mongos nodes: ' + str(len(node_list)))
        Logger.info('Nodes: ' + cluster_config)

        nodes_and_port_indexes = {}
        for host in mongos_hosts_in_ambari:
            nodes_and_port_indexes[host] = 0

        mongos = []
        shards = []

        for index_nodes, node_name in enumerate(node_list, start=0):
            Logger.info('Processing node #: ' + str(index_nodes))
            Logger.info('Node name: ' + node_name)
            pid_file_name = os.path.join(params.pid_db_path,
                                         node_name.split('.')[0] + '_mongos_' +
                                         str(nodes_and_port_indexes[node_name]) + '.pid')
            log_file = os.path.join(params.log_path,
                                    node_name.split('.')[0] + '_mongos_' +
                                    str(nodes_and_port_indexes[node_name]) + '.log')
            db_port = db_ports[nodes_and_port_indexes[node_name]]
            Logger.info('Node PID file name: ' + pid_file_name)
            Logger.info('Node log file: ' + log_file)
            Logger.info('Node db port:' + db_port)
            # Check the mongos status
            mongos_status = self.getMongosStatus(node_name + ':' + db_port)
            shards = mongos_status[1]
            mongos_instance = Mongos(pid_file_name, log_file,db_port, node_name, mongos_status[0])
            mongos.append(mongos_instance)
            nodes_and_port_indexes[node_name] += 1

        return (mongos,shards)

    """Returns a list for this server of shards and server instances of this node:
     [(shard_name,shard_node_list,[InstanceConfig])]
    """
    def getClusterData(self):
        """
        :return Returns a list of shards and nodes that are important for this instance: [(shard_name,shard_node_list,[InstanceConfig])]
        :rtype: list(tuple(str,list(str),list(InstanceConfig))]
        """

        Logger.info('Getting cluster configuration...')
        cluster_config = self.getClusterDefinition()
        db_ports = self.getPorts()
        shard_prefix = self.getShardPrefix()
        db_path = params.db_path

        my_hostname = params.my_hostname
        hosts_in_ambari = self.getHostsInAmbari()

        Logger.info('Cluster definition: ' + cluster_config)
        Logger.info('Database ports: ' + str(db_ports))
        Logger.info('Shard Prefix: ' + shard_prefix)
        Logger.info('My hostname: ' + my_hostname)
        Logger.info('Hosts in ambari: ' + str(hosts_in_ambari))
        Logger.info('DB path: ' + db_path)
        Logger.info('PID path: ' + params.pid_db_path)
        Logger.info('Log path: ' + params.log_path)

        results = []

        # Verify if it is an standalone start
        if (cluster_config == '') & (len(hosts_in_ambari) == 1):
            ## TODO: Implement standalone set up
            Logger.info('Standalone not Implemented yet')
        else:
            # Prepare for cases with just one shard
            if cluster_config == '':
                Logger.info('Cluster with just one shard or is a replicaset with this members: ' + str(hosts_in_ambari))
                cluster_config = reduce(lambda a, b: a + ',' + b, hosts_in_ambari)

            nodes_and_port_indexes = {}
            for host in hosts_in_ambari:
                nodes_and_port_indexes[host] = 0

            cluster_shards = cluster_config.split(';')
            Logger.info('Number of shards: ' + str(len(cluster_shards)))
            for index_shards, shard_nodes in enumerate(cluster_shards, start=0):
                shard_node_list = shard_nodes.split(',')
                shard_name = shard_prefix + str(index_shards)
                Logger.info('Processing shard: ' + shard_name)
                Logger.info('Number of shard nodes: ' + str(len(shard_node_list)))
                Logger.info('Shard nodes: ' + shard_nodes)
                result_nodes = []
                instances_on_this_shard = False
                for index_nodes, node_name in enumerate(shard_node_list, start=0):
                    Logger.info('Processing node #: ' + str(index_nodes))
                    Logger.info('Node name: ' + node_name)

                    is_arbiter = node_name.find('/arbiter') > 0
                    if is_arbiter:
                        Logger.info('Node is an arbiter!')
                        node_name = node_name[:node_name.find('/arbiter')]

                    if node_name == my_hostname:
                        Logger.info('Node is on this server!')
                        instances_on_this_shard = True

                    pid_file_name = os.path.join(params.pid_db_path,
                                                 node_name.split('.')[0] + '_' +
                                                 shard_name + '_' +
                                                 str(nodes_and_port_indexes[node_name]) + '.pid')

                    log_file = os.path.join(params.log_path,
                                            node_name.split('.')[0] + '_' +
                                            shard_name + '_' +
                                            str(nodes_and_port_indexes[node_name]) + '.log')

                    # get db_path
                    final_db_path = os.path.join(db_path,
                                                 node_name.split('.')[0] + '_' +
                                                 shard_name + '_' +
                                                 str(nodes_and_port_indexes[node_name]))

                    db_port = db_ports[nodes_and_port_indexes[node_name]]

                    Logger.info('Node PID file name: ' + pid_file_name)
                    Logger.info('Node log file: ' + log_file)
                    Logger.info('Node db path: ' + final_db_path)
                    Logger.info('Node db port:' + db_port)

                    instance_config = InstanceConfig(shard_name, pid_file_name, final_db_path, log_file,
                                                     db_port, node_name, is_arbiter)

                    result_nodes.append(instance_config)
                    nodes_and_port_indexes[node_name] += 1

                # if len(result_nodes) > 0:
                if instances_on_this_shard:
                    results.append((shard_name, shard_node_list, result_nodes))

        return results


    """
    Receives a list of shards and nodes and returns the status for each one:
         [(shard_name,shard_node_list,[InstanceConfig])]
    Returns a list for this server of shards and server instances of this node:
         [(shard_name,shard_node_list,[InstanceStatus])]
    """
    def getClusterStatus(self, cluster_shard_list):
        """
        :param cluster_shard_list: Receives a list of shards and nodes and returns the status for each one: [(shard_name,shard_node_list,[InstanceConfig])]
        :return: Returns a list for this server of shards and server instances of this node: [(shard_name,shard_node_list,[InstanceStatus])]

        :type cluster_shard_list:  list(tuple(str,list(str),list(InstanceConfig))]
        :rtype: list(tuple(str,list(str),list(InstanceStatus))]
        """
        Logger.info('Getting cluster status...')
        results = []

        Logger.info('Number of shards to process: ' + str(len(cluster_shard_list)))
        for shard in cluster_shard_list:
            Logger.info('Processing shard: ' + shard[0])
            cluster_server_list = shard[2]
            result_nodes = []
            Logger.info('Number of nodes in this shard: ' + str(len(cluster_server_list)))
            for node in cluster_server_list:
                shard_name, pid_file_name, final_db_path, log_file, db_port, hostname, is_arbiter = node

                # Getting 'is_started', 'is_repl_configurated', 'repl_role'
                server = hostname + ":" + db_port
                Logger.info('Processing node: ' + server)

                is_repl_configurated = None
                repl_role = None
                cmd_result = commands.getstatusoutput('mongo ' + server + ' --eval "rs.status()"')

                if cmd_result[0] == 0:
                    is_started = True
                    Logger.info('Server ' + server + ' is on and accepting requests')
                    Logger.info('Checking replicaset configuration for server: ' + server)
                    mongo_result_json = self.parseMongoResult(cmd_result[1])
                    mongoResultOk = str(mongo_result_json[0]['ok']).lstrip().rstrip()
                    Logger.info('Replicaset ok status for ' + server + ':' + mongoResultOk)
                    if mongoResultOk != '0':
                        is_repl_configurated = True
                    else:
                        is_repl_configurated = False

                    if 'members' in mongo_result_json[0]:
                        for member in mongo_result_json[0]['members']:
                            if str(member['name']).lstrip().rstrip() == server:
                                repl_role = str(member['stateStr']).lstrip().rstrip()
                                Logger.info('Replicaset status for ' + server + ' - ' + member['name'] + ' - ' +
                                        repl_role)
                    else:
                        Logger.info('No replicaset configuration the server: ' + server)
                else:
                    is_started = False
                    Logger.info('Server ' + server + ' is off')

                instance_status = InstanceStatus(shard_name, pid_file_name, final_db_path, log_file, db_port, hostname,
                                                 is_arbiter, is_started, is_repl_configurated, repl_role)
                result_nodes.append(instance_status)

            results.append((shard[0], shard[1], result_nodes))
        return results

    def startServer(self, node):
        """
        :type node: InstanceConfig
        :return: None
        """

        # Verbose output
        Logger.info("...")
        Logger.info("Shard Name: " + node.shard_name)
        Logger.info("PID File Name: " + node.pid_file_name)
        Logger.info("DB Path: " + node.final_db_path)
        Logger.info("Port: " + node.db_port)
        Logger.info("Log File Name: " + node.log_file)

        # rm mongo_*.sock
        port = node.db_port
        Execute(format('rm -rf /tmp/mongodb-{port}.sock'), logoutput=True)

        # Creates the db path if it is not there (and if is not blank)
        if len(node.final_db_path) > 0:
            Logger.info("Verifying and creating the db_path if it not exists ...")
            Directory(node.final_db_path,
                      create_parents=True,
                      owner=params.mongodb_user,
                      group=params.mongodb_user_group)

        # Creates the log path if it is not there
        Logger.info("Verifying and creating the log path if it not exists ...")
        log_path = os.path.dirname(node.log_file)
        Directory(log_path,
                  create_parents=True,
                  owner=params.mongodb_user,
                  group=params.mongodb_user_group)

        # Creates the run path if it is not there
        Logger.info("Verifying and creating the run path if it not exists ...")
        run_path = os.path.dirname(node.pid_file_name)
        Directory(run_path,
                  create_parents=True,
                  owner=params.mongodb_user,
                  group=params.mongodb_user_group)

        start_command = self.getStartServerCommand(node)
        return Execute(start_command, logoutput=True)


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
        self.fail_with_error("addShardToMongos method isn't implemented")

    def setupCluster(self,service_list):
        """
        Setup the replicaset and shards conecting with each other

        :param service_list: list(tuple(str,list(str),list(InstanceConfig))]
        :param cluster_status: list(tuple(str,list(str),list(InstanceStatus))]
        :rtype None
        :return: None
        """
        # The standalone cluster will be a replicaset with a primari node only
        Logger.info('Initiating the cluster setup phase ...')

        times_to_try = params.times_to_try
        try_interval = params.try_interval
        my_hostname = params.my_hostname

        cluster_shards_to_configure = service_list
        times = 0
        while (len(cluster_shards_to_configure) > 0) and (times < times_to_try):
            Logger.info('Number of shards to process: ' + str(len(cluster_shards_to_configure)))

            cluster_status = self.getClusterStatus(cluster_shards_to_configure)
            Logger.info(str(cluster_status))
            for shard in cluster_status:
                Logger.info('Processing shard: ' + shard[0])
                Logger.info('Number of shard nodes: ' + str(len(shard[2])))

                shard_nodes = shard[2]
                # Check if every node is up and accepting requests
                if sum(map(lambda node: node.is_started == True, shard_nodes)) == len(shard_nodes):
                    Logger.info('Every node in this shard is up and accepting requests! :)')

                    # Check if there is some node with replicaset configurated
                    if sum(map(lambda node1: node1.is_repl_configurated is True, shard_nodes)) > 0:
                        Logger.info('The are some nodes with replicaset initialized')
                        # Check if the this node is the PRIMARY of the replicaset
                        if sum(map(lambda node2: (node2.repl_role == 'PRIMARY') and (node2.host_name == my_hostname),
                                   shard_nodes)) == 1:
                            # Collect the primary node info
                            Logger.info('This node is the PRIMARY node of the replicaset')
                            primary_node = filter(lambda node3: node3.repl_role == 'PRIMARY',
                                                  shard_nodes)[0]

                            # Add the missing servers
                            nodes_to_add = filter(lambda node4: not node4.is_repl_configurated,
                                                  shard_nodes)
                            Logger.info('We are going to add ' + str(len(nodes_to_add)) + ' nodes to the replica')
                            for node in nodes_to_add:
                                self.addNodeToShard(primary_node, node)

                            # Add shard do mongos list
                            if self.addShardToMongos(shard[0], shard_nodes):
                                cluster_status.pop(cluster_status.index(shard))
                        else:
                            Logger.info('I\'m not the PRIMARY node of the replicaset. Let\'s hope it add us. :)')
                            cluster_status.pop(cluster_status.index(shard))
                    else:
                        Logger.info('There zero nodes with replicaset initialized')
                        # Check if this node is the first node of the replicaset (it must not be an arbiter -
                        # this must be checked in the configuration vadidation)
                        if shard_nodes[0].host_name == my_hostname:
                            Logger.info('I am the PRIMARY node! Starting the sharding/replicaset config')
                            primary_node = shard_nodes[0]
                            nodes_to_add = shard_nodes[1:]
                            self.startShardConfig(primary_node, nodes_to_add)

                            # Add shard do mongos list
                            if self.addShardToMongos(shard[0],shard_nodes):
                                cluster_status.pop(cluster_status.index(shard))
                        else:
                            Logger.info("I'm not the primary by default. Let's hope it add us. :)")
                            cluster_status.pop(cluster_status.index(shard))
                else:
                    Logger.info('Some shard nodes are not up yet. The shard will NOT be initialized')

            # Update cluster_shards_to_configure with the cluster_status shards that are missing
            cluster_shards_to_configure = []
            for shard in cluster_status:
                nodes = []
                for node in shard[2]:
                    nodes.append(InstanceConfig(node.shard_name, node.pid_file_name, node.final_db_path, node.log_file,
                                                node.db_port, node.host_name, node.is_arbiter))
                cluster_shards_to_configure.append((shard[0], shard[1], nodes))

            if len(cluster_status) > 0:
                Logger.info('Waiting ' + str(try_interval) + ' seconds for all instances starts....')
                sleep(try_interval)
            times += 1

    def start(self,env):
        self.configure(env)
        Logger.info("Starting the servers...")

        my_hostname = params.my_hostname
        hosts_in_ambari = self.getHostsInAmbari()
        Logger.info("Current Hostname :" + my_hostname)
        Logger.info("DB Nodes List: " + str(hosts_in_ambari))

        # Start mongod service
        Logger.info("Starting the services on this machine!")
        service_list = self.getClusterData()
        cluster_status = self.getClusterStatus(service_list)

        # Starting servers
        for shard in cluster_status:
            Logger.info("Processing shard: " + shard[0])
            shard_nodes = shard[2]
            Logger.info('Nodes to process: ' + str(len(shard_nodes)))
            for node in shard_nodes:
                Logger.info('Processing node: ' + node.host_name + ':' + node.db_port)
                if node.host_name == my_hostname:
                    Logger.info('Node is on this host')
                    if node.is_started:
                        Logger.info('Node is already started')
                    else:
                        self.startServer(node)

        self.setupCluster(service_list)


    def stop(self, env):
        Logger.info("Stopping services..")
        my_hostname = params.my_hostname
        Logger.info('My hostname: ' + my_hostname)
        cluster_status = self.getClusterStatus(self.getClusterData())
        Logger.info('Shards to process: ' + str(len(cluster_status)))
        for shard in cluster_status:
            Logger.info('Processing shard: ' + shard[0])
            Logger.info('Nodes to process: ' + str(len(shard[2])))
            for node in shard[2]:
                Logger.info('Processing node: ' + node.host_name + node.db_port)
                Logger.info('The node is started: ' + str(node.is_started))
                if (node.host_name == my_hostname):
                    cmd = 'cat ' + node.pid_file_name + ' | xargs kill -9 '
                    try:
                        Execute(cmd, logoutput=True)
                    except:
                        Logger.info('Can not find pid process,skipping this noe')

    def restart(self, env):
        self.configure(env)
        Logger.info("Restarting mongodb conf instance(s)")
        self.stop(env)
        self.start(env)

    def status(self, env):
        self.configure(env)
        my_hostname = params.my_hostname
        Logger.info('My hostname: ' + my_hostname)
        Logger.info("Checking mongodb conf instances status...")
        cluster_status = self.getClusterStatus(self.getClusterData())
        Logger.info('Shards to process: ' + str(len(cluster_status)))
        for shard in cluster_status:
            Logger.info('Processing shard: ' + shard[0])
            Logger.info('Nodes to process: ' + str(len(shard[2])))
            for node in shard[2]:
                Logger.info('Processing node: ' + node.host_name + node.db_port)
                Logger.info('The node is started: ' + str(node.is_started))
                if (node.host_name == my_hostname):
                    check_process_status(node.pid_file_name)

