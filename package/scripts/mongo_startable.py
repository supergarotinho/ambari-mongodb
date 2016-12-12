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

    def status(self, env):
        self.configure(env)
        import logging
        logger = logging.getLogger()

        my_hostname = self.my_hostname
        logger.info('My hostname: ' + my_hostname)
        logger.info("Checking mongo instances status...")
        cluster_status = self.getClusterStatus(self.getClusterData(withThisHostInstancesOnly=True))
        logger.info('Shards to process: ' + str(len(cluster_status)))
        for shard in cluster_status:
            logger.info('Processing shard: ' + shard[0])
            logger.info('Nodes to process: ' + str(len(shard[2])))
            for node in shard[2]:
                logger.info('Processing node: ' + node.host_name + ":" + node.db_port)
                logger.info('The node is started: ' + str(node.is_started))
                logger.info('Pid file :' + node.pid_file_name)
                if node.host_name == my_hostname:
                    logger.info('Checking process id ...')
                    check_process_status(node.pid_file_name)


