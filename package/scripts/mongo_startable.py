from mongo_base import MongoBase
from resource_management.core.logger import Logger
from resource_management.core.resources.system import Execute
from resource_management.libraries.functions import check_process_status

class MongoStartable(MongoBase):
    def start(self,env):
        self.configure(env)
        Logger.info("Starting the servers...")

        my_hostname = self.my_hostname
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
        my_hostname = self.my_hostname
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

    def log(self,info):
        # Execute('echo "' + info + '" >> /var/log/ambari-agent/mongo.log')
        import logging
        logging.info(info)

    def status(self, env):
        # This custom log was added because the normal ambari logging does not work here
        # import logging
        # logger = logging.getLogger('mongo')
        # logger.setLevel(logging.DEBUG)
        # create file handler which logs even debug messages
        # fh = logging.FileHandler('/var/log/ambari-agent/mongo.log')
        # fh.setLevel(logging.DEBUG)
        # logger.addHandler(fh)
        self.log("Initiating mongo status...")
        self.configure(env)
        my_hostname = self.my_hostname
        self.log('My hostname: ' + my_hostname)
        self.log("Checking mongo instances status...")

        # the parameter withThisHostInstancesOnly is being used because when the agent executes this commmand, we do not
        # have the ambari hosts lists available. The ambari config "clusterHostInfo" is not available here
        cluster_status = self.getClusterStatus(self.getClusterData(withThisHostInstancesOnly=True))
        self.log('Shards to process: ' + str(len(cluster_status)))
        for shard in cluster_status:
            self.log('Processing shard: ' + shard[0])
            self.log('Nodes to process: ' + str(len(shard[2])))
            for node in shard[2]:
                self.log('Processing node: ' + node.host_name + ":" + node.db_port)
                self.log('The node is started: ' + str(node.is_started))
                self.log('Pid file :' + node.pid_file_name)
                if node.host_name == my_hostname:
                    self.log('Checking process id ...')
                    check_process_status(node.pid_file_name)


