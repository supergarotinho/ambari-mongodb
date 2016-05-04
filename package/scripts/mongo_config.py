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
