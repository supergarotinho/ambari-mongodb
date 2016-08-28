import os

from resource_management import *
import ambari_simplejson as json # simplejson is much faster comparing to Python 2.6 json module and has the same functions set.

class MongoBase(Script):
    repos_file_path = '/etc/yum.repos.d/mongodb.repo'
    db_file_path = '/etc/mongod.conf'
    config_file_path='/etc/mongod-config.conf'
    mongo_packages = None

    def printOut(content,sep_lines=True):
        sep_line =  "------------------------------------------------------------------------"
        if sep_lines:
            print sep_line
        if isinstance("teste", basestring):
            print content
        else:
            for s in content: print s
        if sep_lines:
            print sep_line

    def installMongo(self, env):
        import params

        env.set_params(params)

        self.install_packages(env)

        if os.path.exists(self.repos_file_path):
            self.printOut("File exists")
        else:
            self.printOut("File not exists")
            File(self.repos_file_path,
                 content=Template("mongodb.repo"),
                mode=0644
                )
        print "Installing mongodb..."
        if self.mongo_packages is not None and len(self.mongo_packages):
            for pack in self.mongo_packages:
                Package(pack)      
        config_path = params.db_path + "/config"
        Execute(format('mkdir -p {config_path}'))

    def configureMongo(self, env):
        import params
        env.set_params(params)
        #db.conf
        self.printOut("Configuring the file: "+self.db_file_path)
        mongod_db_content = InlineTemplate(params.mongod_db_content)   
        File(self.db_file_path, content=mongod_db_content)
        #config.conf
        self.printOut("Configuring the file: "+self.config_file_path)
        mongod_config_content = InlineTemplate(params.mongod_config_content)
        File(self.config_file_path, content=mongod_config_content)
        
        config_path = params.db_path + "/config"
        if os.path.exists(config_path):
            self.printOut("Path exists: " + config_path)
        else:
            Execute(format('mkdir -p {config_path}'))

    def createDB(self, env):
        import params
        env.set_params(params)

        if params.db_name and params.db_pass:
            user_json = {'user': params.db_user, 'pwd': params.db_pass, 'roles': ['readWrite']}
            create_user_cmd = (
                "mongo {db} --eval 'db.getUser(\"{user}\")' | grep -q -w {db}\\.{user} || "
                "mongo {db} --eval 'db.createUser({json});'"
                )
            Execute(create_user_cmd.format(
                db=params.db_name,
                user=params.db_user,
                json=json.dumps(user_json)))
