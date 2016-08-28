import os
from time import sleep
from resource_management import *
from mongo_base import MongoBase

class MongoMaster(MongoBase):
    PID_FILE = '/var/run/mongodb/mongos.pid'

    def install(self, env):
        self.printOut('Install mongodb')

    def configure(self, env):
        self.printOut('Configure mongodb')
        

    def start(self, env):
        sleep(3)
        #waiting for mongod start
        
        import socket
        current_host_name = socket.getfqdn(socket.gethostname())

        import params
        self.configure(env)

        self.printOut('Starting mongo...')

        port = params.tcp_port
        config_port = params.config_server_port

        config = Script.get_config()
        nodes = config['clusterHostInfo']['mongodc_hosts']
        hosts = ''

        for ip in nodes:
            hosts = hosts + ip + ":" + config_port + ","
        hosts = hosts[:-1]
        pid_file = self.PID_FILE
        cmd = format('mongos --configdb {hosts} --bind_ip {current_host_name} -port {port} '
                     '--fork --logappend --logpath  /var/log/mongodb/mongos.log & echo $! > {pid_file} ')

        self.printOut(["Config nodes from ambari: " + ",".join(nodes),
                       "Hosts for mongos: " + hosts,
                       "Mongos port: ",
                       "PID File: " + pid_file,
                       "Current hostname: " + current_host_name
                       ])

        Execute('rm -rf /tmp/mongodb-' + str(port) + '.sock',logoutput=True)
        Execute(cmd,logoutput=True)
        len_port=len(params.db_ports)
                
        # import socket
        # current_host_name=socket.getfqdn(socket.gethostname())
        #
        # #Add Shards to the Cluster
        # shard_param =''
        #
        # node_group = ','.join(config['clusterHostInfo']['mongodb_hosts'])
        #
        # print node_group
        # groups = node_group.split(';')
        # for index_g,item_g in enumerate(groups,start=0):
        #     db_hosts = item_g.split(',')
        #     shard_prefix = params.shard_prefix
        #     len_host=len(db_hosts)
        #     for index,item in enumerate(db_hosts,start=0):
        #         current_shard=index
        #         current_index=0
        #         shard_nodes = ''
        #         while(current_index<len_port):
        #             current_index_host=db_hosts[current_shard]
        #             current_index_port=params.db_ports[current_index]
        #             shard_nodes = shard_nodes + format('{current_index_host}:{current_index_port},')
        #             current_index = current_index + 1
        #             current_shard = (current_shard + 1)%len_host
        #         shard_name= shard_prefix + str(index)
        #         shard_nodes=shard_nodes[:-1]
        #         basic_port = params.db_ports[0]
        #         shard_param = shard_param + format('sh.addShard( \"{shard_name}/{shard_nodes}\" )\n')
        # cmd = format('mongo --host {current_host_name} --port {port} <<EOF\n  {shard_param} \nEOF\n')
        # File('/var/run/mongos.sh',
        #      content=cmd,
        #      mode=0755
        # )
        # sleep(5)
        # Execute('/var/run/mongos.sh',logoutput=True,try_sleep=3,tries=5)


    def stop(self, env):
        #no need stop
        print("stop")
        pid_file = self.PID_FILE
        cmd =format('cat {pid_file} | xargs kill -9 ')
        try:
            Execute(cmd,logoutput=True)
        except:
            print 'can not find pid process,skip this'

    def restart(self, env):
        #no need restart
        print("restart")
        self.stop(env)
        self.start(env)

    def status(self, env):
       #use built-in method to check status using pidfile
       check_process_status(self.PID_FILE)  

if __name__ == "__main__":
    MongoMaster().execute()
