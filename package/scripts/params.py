import socket
from resource_management.core.environment import *

## TODO: Must change to right ones
"""
# Textarea fields for custom mongodb.conf file for config server;mongod and mongos instances
mongoconf_config_content = default('configurations/mongo-conf/conf_file', '')
mongodb_config_content = default('configurations/mongod/conf_file', '')
mongos_config_content = default('configurations/mongos/conf_file', '')

# Define the mongod cluster architecture
mongod_cluster_definition = default('configurations/mongod/cluster_definition', '')
# Define the mongo-conf and mongos instances
mongoconf_cluster_definition = default('configurations/mongo-conf/cluster_definition', '')
mongos_cluster_definition = default('configurations/mongos/cluster_definition', '')

# Avaliable ports for each type of instance (config server;mongod and mongos)
mongod_ports = default('configurations/mongod/ports', '27025,27030-27035')
mongoconf_ports = default('configurations/mongo-conf/ports', '27019-27021')
mongos_ports = default('configurations/mongos/ports', '27017,27018')

# Textfield for database path prefix
db_path = default('configurations/mongodb/db_path', '/var/lib/mongodb')
# Textfield for log path prefix
log_path = default('configurations/mongodb/log_path', '/var/log/mongodb')
# Textfield for PID file path prefix
pid_db_path = default('configurations/mongodb/pid_db_path', '/var/run/mongodb')

# Interval to wait before trying to configure the cluster
try_interval = default('configurations/mongodb/try_interval', '10')
# Times to try to configure the cluster
times_to_try = default('configurations/mongodb/times_to_try', '10')

# Mongodb user and group that will execute the instances
mongodb_user = default('configurations/mongodb/mongodb_user', 'mongodb')
mongodb_user_group = default('configurations/mongodb/mongodb_user_group', 'mongodb')
"""
mongoconf_config_content = ''
mongodb_config_content = ''
mongos_config_content = ''

mongod_cluster_definition = "mandachuva.falometro.com.br," \
            "batatinha01.falometro.com.br," \
            "batatinha02.falometro.com.br;" \
            "mandachuva.falometro.com.br," \
            "mandachuva.falometro.com.br/arbiter," \
            "batatinha02.falometro.com.br;" \
            "batatinha02.falometro.com.br," \
            "batatinha01.falometro.com.br," \
            "batatinha01.falometro.com.br," \
            "mandachuva.falometro.com.br/arbiter," \
            "mandachuva.falometro.com.br"

mongoconf_cluster_definition = ''
mongos_cluster_definition = 'mandachuva.falometro.com.br,mandachuva.falometro.com.br'

mongod_ports = '27025,27030-27035'
mongoconf_ports = '27019-27021'
mongos_ports = '27017,27018'

mongod_shard_prefix='shard'
mongoconf_shard_prefix='configReplSet'

db_path = '/var/lib/mongodb'
log_path='/var/log/mongodb'
pid_db_path = '/var/run/mongodb'

try_interval = 10
times_to_try = 10

mongodb_user = 'mongodb'
mongodb_user_group = 'mongodb'

my_hostname = socket.getfqdn(socket.gethostname())


"""
Referencia para teste:

        self.hosts_in_ambari = "mandachuva.falometro.com.br,batatinha01.falometro.com.br,batatinha02.falometro.com.br".split(',')
        self.hosts_in_ambari = "localhost".split(',')
        self.hosts_in_ambari = \
            "mandachuva.falometro.com.br," \
            "batatinha01.falometro.com.br," \
            "batatinha02.falometro.com.br;" \
            "mandachuva.falometro.com.br/arbiter," \
            "mandachuva.falometro.com.br," \
            "batatinha02.falometro.com.br;" \
            "batatinha02.falometro.com.br," \
            "batatinha01.falometro.com.br," \
            "batatinha01.falometro.com.br," \
            "mandachuva.falometro.com.br"

"""