import os
from time import sleep
from resource_management import *
from mongo_base import MongoBase
from resource_management.core.logger import Logger

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
        self.printOut("start mongodb")

        import socket
        current_host_name=socket.getfqdn(socket.gethostname())
        
        config = Script.get_config()
        shard_prefix = params.shard_prefix
        
        db_hosts = config['clusterHostInfo']['mongodb_hosts']
        db_ports = params.db_ports
        node_group = params.node_group

        len_host=len(db_hosts)
        len_port=len(db_ports)
        self.printOut(["Current Hostname :" + current_host_name,
                       "DB Nodes List: ",
                       db_hosts])

        #Start mongod service
        shard_name, pid_file_name, final_db_path, db_port = self.getProcessData()
        self.startServer(shard_name, pid_file_name, final_db_path, db_port)

        self.printOut('Sleep waiting for all mongod starts....')
        sleep(20)

        if node_group =='':
            ## All of the hosts will be replicas of the same shard
            index = db_hosts.index(current_host_name)
            shard_name = shard_prefix + "0"

            if index == 0:
                self.configureReplicaServers(shard_name,db_hosts)

        else:
            cluster_shards = node_group.split(';')
            for index_shards, shard_nodes in enumerate(cluster_shards, start=0):
                ## All of the hosts will be replicas of the same shard
                shard_node_list = shard_nodes.split(',')
                index = shard_node_list.index(current_host_name)
                shard_name = shard_prefix + str(index_shards)

                if index == 0:
                    self.configureReplicaServers(shard_name, shard_node_list)

    ## Returns: (shard_name, pid_file_name, final_db_path, db_port)
    def getProcessData(self):
        import socket
        current_host_name=socket.getfqdn(socket.gethostname())
        import params
        config = Script.get_config()
        db_hosts = config['clusterHostInfo']['mongodb_hosts']
        shard_prefix = params.shard_prefix
        db_ports = params.db_ports
        node_group = params.node_group
        db_path = params.db_path

        if node_group == '':
            ## All of the instances will be replicas of the same shard
            shard_name = shard_prefix + "0"

            for index, item in enumerate(db_hosts, start=0):
                if item == current_host_name:
                    pid_file_name = shard_name + '_0'  ## TODO: Prepare for multiple instances per node
                    # get db_path
                    ## TODO: prepare for multiple instances per node
                    final_db_path = db_path + '/' + current_host_name.split('.')[0] + '_0'
                    return (shard_name, pid_file_name, final_db_path, db_ports[0])
                    ## TODO: Prepare for multiple instances per node - Check if the name appear twice in the node_group and get the port number and index
        else:
            cluster_shards = node_group.split(';')
            for index_shards, shard_nodes in enumerate(cluster_shards, start=0):
                shard_node_list = shard_nodes.split(',')
                for index_nodes, node_name in enumerate(shard_node_list, start=0):
                    if node_name == current_host_name:
                        shard_name = shard_prefix + str(index_shards)
                        pid_file_name = shard_name + '_0'  ## TODO: Prepare for multiple instances per node
                        # get db_path
                        final_db_path = db_path + '/' + current_host_name.split('.')[
                            0] + '_0'  ## TODO: prepare for multiple instances per node
                        return (shard_name, pid_file_name, final_db_path, db_ports[0])
                        ## TODO: Prepare for multiple instances per node - Check if the name appear twice in the node_group and get the port number and index

    def startServer(self,shard_name,pid_file_name,final_db_path,port):
        import params

        # Verbose output
        self.printOut(["Shard Name: " + shard_name,
               "PID File Name: " + pid_file_name,
               "DB Path: " + final_db_path,
               "Port: " + port])

        # rm mongo_*.sock
        Execute(format('rm -rf /tmp/mongodb-{port}.sock'), logoutput=True)

        if os.path.exists(final_db_path):
            self.printOut("Path exists:" + final_db_path)
        else:
            Execute(format('mkdir -p {final_db_path}'), logoutput=True)

        log_file = params.log_path + '/' + shard_name + '.log'
        pid_file = params.pid_db_path + '/' + pid_file_name + '.pid'

        self.printOut(["Log File with path: " + shard_name,
                       "PID File with path: " + pid_file_name])

        Execute(format(
            'mongod -f /etc/mongod.conf --shardsvr  -replSet {shard_name} -port {port} -dbpath {final_db_path} -oplogSize 100 -logpath {log_file} -pidfilepath {pid_file}')
                , logoutput=True)

    def configureReplicaServers(self,shard_name,db_hosts):
        ## Getting important params and configuration
        import socket
        current_host_name = socket.getfqdn(socket.gethostname())
        import params
        db_ports = params.db_ports
        len_host = len(db_hosts)

        members = ''
        current_index = 0
        while (current_index < len_host):
            current_host = db_hosts[current_index]
            current_port = db_ports[0] ## TODO: It not yet prepared for more than one server name in the list
            members = members + '{_id:' + format('{current_index},host:"{current_host}:{current_port}"')
            if current_index == 0:
                members = members + ',priority:2'
            members = members + '},'
            current_index = current_index + 1

        # add arbiter
        #current_port = params.arbiter_port
        #members = members + '{_id:' + format(
        #    '{current_index},host:"{current_host_name}:{current_port}"') + ',arbiterOnly: true},'
        members = members[:-1]

        replica_param = 'rs.initiate( {_id:' + format('"{shard_name}",version: 1,members:') + '[' + members + ']})'

        cmd = format('mongo --host {current_host_name} --port 27017 <<EOF \n{replica_param} \nEOF\n')
        self.printOut(['Configure Replica command: ',
                       cmd])
        File('/var/run/mongo_config.sh',
             content=cmd,
             mode=0755
             )
        Execute('/var/run/mongo_config.sh', logoutput=True)

    def stop(self, env):
        print "stop services.."
        import params                
        db_ports = params.db_ports       
        for index_p,p in enumerate(db_ports,start=0):                   
            shard_name = params.shard_prefix + str(index_p)                         
            pid_file = params.pid_db_path + '/' + shard_name + '.pid'                  
            cmd =format('cat {pid_file} | xargs kill -9 ')
            try:
               Execute(cmd,logoutput=True)
            except:
               print 'can not find pid process,skip this'
        #stop arbiter       
        shard_name = params.shard_prefix + '_arbiter'                         
        pid_file = params.pid_db_path + '/' + shard_name + '.pid'                  
        cmd =format('cat {pid_file} | xargs kill -9 ')
        try:
            Execute(cmd,logoutput=True)
        except:
            print 'can not find pid process,skip this'

    def restart(self, env):
        self.configure(env)
        print "restart mongodb"
        #Execute('service mongod restart')
        #self.status(env)
        self.stop(env)
        self.start(env)

    def status(self, env):
        print "checking status..."
        
        import params                    
        db_ports = params.db_ports     
        for index_p,p in enumerate(db_ports,start=0):                   
            shard_name = params.shard_prefix + str(index_p)                         
            pid_file = params.pid_db_path + '/' + shard_name + '.pid'
            check_process_status(pid_file)            

if __name__ == "__main__":
    MongoMaster().execute()
