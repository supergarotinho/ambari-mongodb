### An Ambari Stack for MongoDB Cluster
Ambari stack for easily installing and managing MongoDB on HDP cluster with any kind of cluster architecture.

**Author:** [Anderson Santos](https://br.linkedin.com/in/andersonrss)

####Features

- Auto install mongodb in the following ways:
  - As a sharding cluster
  - As a replicaset
- Auto install the following components;
  - Mongod server instances
  - Mongo config server instances
  - Mongos (Query router) server instances
  - A client wrapper to be used to connect to the cluster
- Supports executing more than one instance of the same server type per host
  - This is useful when the number of hosts are limited
- Shard architecture configuration:
  - Configure witch instances will be in witch shard
  - Configure witch instances will act as an arbiter
- Support cluster scaling:
  - Adding new shards to the cluster
  - Adding new instances to the shard
  - Adding new instances to the shard that will execute in the same host
- It has a service advisor that will warn if the cluster architecture is not recommendable
  - It also validates the configuration
  - The validation list is [here](docs/validator.md)

#### MongoDB Replicaset Cluster Architecture 

![Image](../master/docs/images/mongodb-repl-cluster.png?raw=true)

#### MongoDB Sharding Cluster Architecture 

![Image](../master/docs/images/mongodb-shard-cluster.png?raw=true)

###Assumptions

- Ambari is installed and running.
- No previous installations of Mongo DB exist. If there any, you can either remove it or rename it.

###Setup

Follow given step to install and manage Mongo DB using Ambari.

1. Connect to the VM via SSH (password hadoop for sandbox image) and start Ambari server
```
ssh root@ambari.machine
```

2. To deploy the Mongo DB, run below
```
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
sudo git clone https://github.com/maocorte/ambari-tachyon-service.git  /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/MongoDB
```

3. Restart ambari server
```
#sandbox
service ambari restart

#non sandbox
sudo service ambari-server restart
```

4. Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:
5. On bottom left -> Actions -> Add service -> check MongoDB -> Next -> Next -> Next -> Deploy

```
![Image](../master/screenshots/addservice.png?raw=true)
![Image](../master/screenshots/assingnslave.png?raw=true)
![Image](../master/screenshots/customize.png?raw=true)
![Image](../master/screenshots/review.png?raw=true)

maybe there is something waring
![Image](../master/screenshots/warning.png?raw=true)
just restart the wrong  service
![Image](../master/screenshots/restart_warning.png?raw=true)
```

6. On successful deployment you will see the MongoDB as part of Ambari stack and will be able to start/stop the service from here:

![Image](../master/screenshots/mongosummary.png?raw=true)

####mongodb port
- mongos port 30000
- mongo config port 20000
- mongo replica port 27017,27018,27019

####mongodb scale out
config param node_group.new add hosts is new group.split by ;
![Image](../master/screenshots/01_modify_mongodb_config.png?raw=true)
![Image](../master/screenshots/02_add_new_hosts.png?raw=true)
![Image](../master/screenshots/03_install_options.png?raw=true)
![Image](../master/screenshots/04_confirm_hosts.png?raw=true)
![Image](../master/screenshots/05_add_salves_service.png?raw=true)
![Image](../master/screenshots/06_review.png?raw=true)
![Image](../master/screenshots/07_install_start_test.png?raw=true)
restart mongodb
![Image](../master/screenshots/08_restart_mongodb_config.png?raw=true)
![Image](../master/screenshots/10_mongodb_summary.png?raw=true)

maybe you just add one host
![Image](../master/screenshots/A1_modify_config_add_new_host.png?raw=true)
![Image](../master/screenshots/A2_host_add_service.png?raw=true)
![Image](../master/screenshots/A3_host_add_service_select_mongodb.png?raw=true)
![Image](../master/screenshots/A4_install_mongodb.png?raw=true)
![Image](../master/screenshots/A5_restart_all_mongodb_service.png?raw=true)
![Image](../master/screenshots/A6_mongodb_summary.png?raw=true)

####Rest Manage

- One benefit to wrapping the component in Ambari service is that you can now monitor/manage this service remotely via REST API

```
export SERVICE=MONGODB
export PASSWORD=admin
export AMBARI_HOST="your_ambari_hostname"
export CLUSTER="your_ambari_cluster_name"

#get service status
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X GET http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#start service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Start $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#stop service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
```

#### Remove Mongo service

- To remove the MongoDB:
  - Stop the service via Ambari
  - Delete the service

    ```
    curl -u admin:admin -i -H 'X-Requested-By: ambari' -X DELETE http://replace_with_your_ambari_hostname.com:8080/api/v1/clusters/ambari_cluster_name/services/MONGODB
    ```
  - Remove artifacts

    ```
    rm -rf /var/lib/ambari-server/resources/stacks/HDP/2.4/services/mongo-ambari
    ```
  - Restart Ambari
    ```
    service ambari restart
    ```

###References:

- This is a 99% rewritten version of the "geniuszhe" version: https://github.com/cas-bigdatalab/ambari-mongodb-cluster
