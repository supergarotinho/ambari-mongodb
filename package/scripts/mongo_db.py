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
        db_hosts = config['clusterHostInfo']['mongodb_hosts']
        len_host=len(db_hosts)
        len_port=len(params.db_ports)
        print "hostname :" + current_host_name
        print "db nodes list"
        print db_hosts
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
                   Execute(format('mongod -f /etc/mongod.conf --shardsvr  -replSet {shard_name} -port {p} -dbpath {db_path} -oplogSize 100 -logpath {log_file} -pidfilepath {pid_file}')
                           ,logoutput=True)
        sleep(5)
        print 'sleep waiting for all mongod started'
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
                replica_param ='rs.initiate( {_id:'+format('"{shard_name}",version: 1,members:') + '[' + members + ']})'
        
        cmd = format('mongo --host {current_host_name} --port 27017 <<EOF \n{replica_param} \nEOF\n')
            #Execute(cmd,logoutput=True)
        File('/var/run/mongo_config.sh',
             content=cmd,
             mode=0755
        )
        Execute('/var/run/mongo_config.sh',logoutput=True)

    def stop(self, env):
        print "stop services.."
        import params                
        
        for index_p,p in enumerate(params.db_ports,start=0):                   
            #get shard_name
            shard_name = params.shard_prefix + str(index_p)                         
            pid_file = params.pid_db_path + '/' + shard_name + '.pid'                  
            cmd =format('cat {pid_file} | xargs kill -9 ')
            Execute(cmd,logoutput=True)             

    def restart(self, env):
        self.configure(env)
        print "restart mongodb"
        #Execute('service mongod restart')
        self.stop(env)
        self.start(env)

    def status(self, env):
        import params
        print "checking status..."
        
        for index_p,p in enumerate(params.db_ports,start=0):                   
            #get shard_name
            shard_name = params.shard_prefix + str(index_p)                         
            pid_file = params.pid_db_path + '/' + shard_name + '.pid'                  
            check_process_status(pid_file)              


if __name__ == "__main__":
    MongoMaster().execute()
