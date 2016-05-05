import os
from time import sleep
from resource_management import *
from mongo_base import MongoBase

class MongoMaster(MongoBase):
    mongo_packages = ['mongodb-org']
    PID_FILE = '/var/run/mongodb/mongos.pid'

    def install(self, env):
        print 'install mongodb'

    def configure(self, env):
        print 'configure mongodb'
        

    def start(self, env):
        import params
        self.configure(env)
        #print "start mongodb"
        Execute('rm -rf /tmp/mongodb-30000.sock',logoutput=True)
        config = Script.get_config()
        nodes = config['clusterHostInfo']['mongodc_hosts']
        hosts = ''
        for ip in nodes:
            hosts = hosts + ip + ":20000,"
        hosts = hosts[:-1]
        pid_file = self.PID_FILE
        port = params.mongos_tcp_port
        cmd = format('mongos -configdb {hosts} -port {port} -logpath  /var/log/mongodb/mongos.log & echo $! > {pid_file} ')
        Execute(cmd,logoutput=True)        
        len_port=len(params.db_ports)
        len_host=len(nodes)
        
        import socket
        current_host_name=socket.getfqdn(socket.gethostname())
        db_hosts = config['clusterHostInfo']['mongodb_hosts']
        #Add Shards to the Cluster        
        shard_param =''
        
        for index,item in enumerate(db_hosts,start=0):
            current_shard=index
            current_index=0
            shard_nodes = ''
            while(current_index<len_port):
                #print db_hosts[current_shard] + ":" + port[current_index]
                current_index_host=db_hosts[current_shard]
                current_index_port=params.db_ports[current_index]
                shard_nodes = shard_nodes + format('{current_index_host}:{current_index_port},')
                current_index = current_index + 1
                current_shard = (current_shard + 1)%len_host
            shard_name=params.shard_prefix+ str(index)
            shard_nodes=shard_nodes[:-1]
            basic_port = params.db_ports[0]
            shard_param = shard_param + format('sh.addShard( \"{shard_name}/{shard_nodes}\" )\n')
            #shard_param = shard_param + format('sh.addShard( \"{shard_name}/{item}:{basic_port}\" )\n')
        cmd = format('mongo --host {current_host_name} --port {port} <<EOF\n  {shard_param} \nEOF\n')
        #Execute(cmd,logoutput=True)
        File('/var/run/mongos.sh',
             content=cmd,
             mode=0755
        )
        sleep(5)
        Execute('/var/run/mongos.sh',logoutput=True)


    def stop(self, env):
        #no need stop
        print("stop")
        pid_file = self.PID_FILE
        cmd =format('cat {pid_file} | xargs kill -9 ')
        Execute(cmd,logoutput=True)

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
