import os
from time import sleep
from resource_management import *
from mongo_base import MongoBase
from status import check_service_status

class MongoConfigServer(MongoBase):
    PID_CONFIG_FILE = '/var/run/mongodb/mongod-config.pid'

    def install(self, env):
        #no need
        self.printOut('install mongodb')

    def configure(self, env):
        import params
        env.set_params(params)
        self.configureMongo(env)

    def start(self, env):
        self.configure(env)

        import socket
        current_host_name = socket.getfqdn(socket.gethostname())

        Logger.initialize_logger()

        import params
        env.set_params(params)
        config_port = params.config_server_port

        self.printOut(["Start mongodb Config Server",
                       "Current Hostname: " + current_host_name,
                       "Config server port: " + config_port])
        Execute('rm -rf /tmp/mongodb-' + config_port + '.sock',logoutput=True,try_sleep=3,tries=5)
        Execute('mongod --configsvr --pidfilepath ' + self.PID_CONFIG_FILE +
                ' --bind_ip '+current_host_name + ' --port '+config_port +
                ' --fork --logappend --logpath /var/log/mongodb/mongod.log',logoutput=True,try_sleep=3,tries=5)
                

    def stop(self, env):
        self.printOut("Stop Services...")
        pid_config_file=self.PID_CONFIG_FILE        
        cmd =format('cat {pid_config_file} | xargs kill -9 ')
        try:
            Execute(cmd,logoutput=True)
        except:
            self.printOut('can not find pid process,skip this')

    def restart(self, env):
        self.configure(env)
        self.printOut("restart mongodb")
        self.stop(env)
        self.start(env)

    def status(self, env):
        self.printOut("checking status...")
        check_process_status(self.PID_CONFIG_FILE)


if __name__ == "__main__":
    MongoConfigServer().execute()
