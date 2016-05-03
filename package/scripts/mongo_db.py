import os
from time import sleep
from resource_management import *
from mongo_base import MongoBase

class MongoMaster(MongoBase):
    mongo_packages = ['mongodb-org']
    

    def install(self, env):
        import params
        env.set_params(params)
        self.installMongo(env)

    def configure(self, env):
        import params
        env.set_params(params)
        self.configureMongo(env)

    def start(self, env):
        import params
        self.configure(env)
        print "start mongodb"
        
        import socket
        current_host_name=socket.getfqdn(socket.gethostname())
        config = Script.get_config()
        db_hosts = config['clusterHostInfo']['mongodb_db_hosts']
        len_host=len(db_hosts)
        len_port=len(params.db_ports)
        #get shard_name
        for index,item in enumerate(db_hosts,start=0):
            if item ==current_host_name:
                #foreach db_ports
                for index_p,p in enumerate(params.db_ports,start=0):
                   #rm mongo_*.sock
                   Execute(format('rm -rf /tmp/mongodb-{p}.sock'),logoutput=True)
                   #get shard_name
                   shard_name = params.shard_prefix + str((index-index_p)%len_host)      
                   #get db_path                   
                   db_path = params.db_path + '/' + shard_name
                   
                   if os.path.exists(db_path):
                       print "File exists"
                   else:
                       Execute(format('mkdir -p {db_path}'),logoutput=True)
                   log_file = params.log_path + '/' + shard_name + '.log'
                   pid_file = params.pid_db_path + '/' + shard_name + '.pid'
                   Execute(format('mongod -f /etc/mongod.conf -shardsvr -replSet {shard_name} -port {p} -dbpath {db_path} -oplogSize 100 -logpath {log_file} -pidfilepath {pid_file}')
                           ,logoutput=True)

    def stop(self, env):
        print "stop services.."
        import params                
        
        import socket
        current_host_name=socket.getfqdn(socket.gethostname())
        len_host=len(host)
        len_port=len(params.db_ports)
        #get shard_name
        for index,item in enumerate(host,start=0):
            if item ==current_host_name:
                #foreach db_ports
                for index_p,p in enumerate(params.db_ports,start=0):                   
                   #get shard_name
                   shard_name = params.shard_prefix + str((index-index_p)%len_host)                         
                   pid_file = params.pid_db_path + '/' + shard_name + '.pid'                  
                   cmd =format('cat {pid_db_file} | xargs kill -9 ')
                   Execute(cmd,logoutput=True)                

    def restart(self, env):
        self.configure(env)
        print "restart mongodb"
        #Execute('service mongod restart')
        stop(self,env)
        start(self,env)

    def status(self, env):
        print "checking status..."
        #Execute('service mongod status')
        
        #check_process_status(self.PID_CONFIG_FILE)
        import socket
        current_host_name=socket.getfqdn(socket.gethostname())
        len_host=len(host)
        len_port=len(params.db_ports)
        #get shard_name
        for index,item in enumerate(host,start=0):
            if item ==current_host_name:
                #foreach db_ports
                for index_p,p in enumerate(params.db_ports,start=0):                   
                   #get shard_name
                   shard_name = params.shard_prefix + str((index-index_p)%len_host)                         
                   pid_file = params.pid_db_path + '/' + shard_name + '.pid'                  
                   check_process_status(self.PID_DB_FILE)              


if __name__ == "__main__":
    MongoMaster().execute()
