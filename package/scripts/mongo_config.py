import os
from time import sleep
from resource_management import *
from mongo_base import MongoBase

class MongoMaster(MongoBase):
    mongo_packages = ['mongodb-org']
    PID_CONFIG_FILE = '/var/run/mongodb/mongod-config.pid'

    def install(self, env):
        #no need
        print 'install mongodb'

    def configure(self, env):
        import params
        env.set_params(params)
        self.configureMongo(env)

    def start(self, env):
        self.configure(env)
        print "start mongodb"
        Execute('rm -rf /tmp/mongodb-20000.sock',logoutput=True)
        Execute('mongod -f /etc/mongod-config.conf')
        
        import params
        config = Script.get_config()
        db_hosts = config['clusterHostInfo']['mongodb_db_hosts']
        len_port=len(params.db_ports)
        replica_param=''
        import socket
        current_host_name=socket.getfqdn(socket.gethostname())
        #init Replica Set
        for index,item in enumerate(db_hosts,start=0):         
            shard_name= params.shard_prefix + str(index)
            
            members =''
            current_index=0
            current_shard=index
            while(current_index<len_port):
                current_host = db_hosts[current_shard]
                current_port = params.db_ports[current_index]
                members = members+ '{_id:'+format('{current_index},host:"{current_host}:{current_port}"') + '},'
                current_index = current_index + 1
                current_shard = (current_shard + 1)%len(db_hosts)
            members=members[:-1]
            if item == current_host_name:            
                replica_param ='rs.initiate( {_id:'+format('"{shard_name}",version: 1,configsvr:true,members:') + '[' + members + ']})'
        
        cmd = format('mongo --host {current_host_name} --port 27017 <<EOF \n{replica_param} \nEOF\n')
            #Execute(cmd,logoutput=True)
        File('/var/run/mongo_config.sh',
             content=cmd,
             mode=0755
        )
        Execute('/var/run/mongo_config.sh',logoutput=True)

    def stop(self, env):
        print "stop services.."
        pid_config_file=self.PID_CONFIG_FILE        
        cmd =format('cat {pid_config_file} | xargs kill -9 ')
        Execute(cmd,logoutput=True)              

    def restart(self, env):
        self.configure(env)
        print "restart mongodb"
        stop(self,env)
        start(self,env)

    def status(self, env):
        print "checking status..."
        check_process_status(self.PID_CONFIG_FILE)


if __name__ == "__main__":
    MongoMaster().execute()
