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
        self.configureMongoClient()
        env.set_params(params)
        File(self.client_config_path,
             content=Template("mongoclient.conf.j2"),
             mode=0644
             )

    def configureMongoClient(self):
        """
            Configure the params needed to create the config template
        """
        Logger.info("Configuring Mongo Client...")
        hosts_str = ""

        Logger.info("Getting Mongos List...")
        mongosList, shards = self.getMongosList()

        Logger.info("Getting MongoD cluster data and status...")
        mongodList = self.getMongoDClusterStatus()

        Logger.info("Mongos Query Routes instances: " + str(len(mongosList)))
        Logger.info("Mongod Shards: " + str(len(mongodList)))

        # It is a sharding cluster?
        if len(mongosList) > 0:
            Logger.info("It is a sharding cluster. Pointing the host and ports to the mongos instances")
            hosts_str = reduce(lambda x, y: x + "," + y, map(lambda x: x.host_name + ":" + str(x.db_port), mongosList))
        # It is a replicaset cluster?
        elif len(mongodList) == 1:
            candidate_hosts = mongodList[0][2]

            # Check if it is a standalone deployment
            if len(candidate_hosts) == 1:
                Logger.info("It is a standalone cluster. Pointing the host and ports to the mongod instance")
                hosts_str = candidate_hosts[0].host_name + ':' + candidate_hosts[0].db_port
            else:
                Logger.info("It is a replicaset. Pointing the host and ports to the probably primary mongod instance")
                # Check if there is a PRIMARY host somewhere in the shard
                primaryReplHosts = filter(lambda node: node.repl_role == 'PRIMARY', candidate_hosts)
                if len(primaryReplHosts) == 0:
                    Logger.info("We found a PRIMARY active instance")
                    hosts_str = candidate_hosts[0].host_name + ':' + candidate_hosts[0].db_port
                else:
                    Logger.info("We do NOT found a PRIMARY active instance. Pointing to the most probable")
                    hosts_str = primaryReplHosts[0].host_name + ':' + primaryReplHosts[0].db_port

        # Change the config file with hosts information
        params.mongos_hosts = hosts_str


if __name__ == "__main__":
    MongoClient().execute()
