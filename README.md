### An Ambari Stack for MongoDB Cluster
Ambari stack for easily installing and managing MongoDB on HDP cluster with any kind of cluster architecture.

**Author:** [Anderson Santos](https://br.linkedin.com/in/andersonrss)

#### Features

- Auto install mongodb in the following ways:
  - As a sharding cluster
  - As a replicaset
  - As a standalone deploy
- Auto install the following components;
  - Mongod server instances
  - Mongo config server instances
  - Mongos (Query router) server instances
  - A client wrapper to be used to connect to the cluster
- Supports executing more than one instance of the same server type per host
  - This is useful when the number of hosts are limited
  - In order to do that, you must specify more than one port in the port list configuration for that instance type
- Supports a very flexible port configuration string
  - Eg.: 27019,27020,27025-27027 
- Shard architecture configuration:
  - Configure witch instances will be in witch shard
  - Configure witch instances will act as an arbiter
- Automatically configure the shards adding the nodes to it
  - Automatically detect the primary host to do it
- Automatically add the shard to the mongos (Query Router) shard list
- Support cluster scaling:
  - Adding new shards to the cluster
  - Adding new instances to the shard
  - Adding new instances to the shard that will execute in the same host
- It has a service advisor that will warn if the cluster architecture is not recommendable
  - It also validates the configuration
  - The validation list is [here](docs/validator.md)
- A client script that automatically detects the mongo server that is online and must be used
  - It automatically detects the hostname and port of the available servers
  - It considers the architecture before deciding which server
  - It checks if the server is on before trying to connect
  - It can be called using ```mogok```
  - You can also use any mongo paramer such as: ```mogok --user admin --eval 'rs.status()'```

#### Features in development stage

- Add logOpSize config option 
- An alert when the cluster is up but the shards are not 100% ok
  - If there are missing nodes on it
- An alert when the shards are not in the mongos (Query Router) shard list
- An command to re-configure the cluster:
  - Adding the missing nodes to the shard
  - Adding the missing shards to the mongos list

#### Future Features and development

We are needing help for these features. We have already developed some draft scripts and solutions for it.

- **Testing**
  - The tests for the service_advisor script
  - An docker instance to setup an testing environment and execute the integrated tests for CentOS and Redhat distros 
- Few modifications to support other linux distros
  - And docker instances to execute the integrated tests
- **A metrics monitor** to send several metrics from the mongo instances to ambari
  - And the ambari metrics screen :)
- **Useful Tasks:**  
  - A command to delete nodes and shards
  - A command to change the shard order
  - A command to backup the databases
  - A command to restore the databases

#### MongoDB Replicaset Cluster Architecture 

![Image](docs/images/mongodb-repl-cluster.png?raw=true)

#### MongoDB Sharding Cluster Architecture 

![Image](docs/images/mongodb-shard-cluster.png?raw=true)

### Assumptions

- Ambari is installed and running.
- No previous installations of Mongo DB exist. If there any, you can either remove it or rename it.

### Setup

Follow given step to install and manage Mongo DB using Ambari.

1. Connect to the VM via SSH (password hadoop for sandbox image) and start Ambari server
```bash
ssh root@ambari.machine
```

2. To deploy the Mongo DB, run below
```bash
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
sudo git clone https://github.com/maocorte/ambari-tachyon-service.git  /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/MongoDB
```

3. Restart ambari server
```bash
#sandbox
service ambari restart

#non sandbox
sudo service ambari-server restart
```

4. Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:
5. On bottom left -> Actions -> Add service -> check MongoDB -> Next -> Next -> Next -> Deploy

    - The images of the installation sequence are [here](docs/setup.md)

6. On successful deployment you will see the MongoDB as part of Ambari stack and will be able to start/stop the service from here:

![Image](docs/images/summary.png?raw=true)

> **Important Notes:**
> - It is recommended to start all nodes of the same component type together
> - If you are not going to restart all components at the same time, use the following recommended order:
>   1. Start the mongo config servers first
>   2. The start the mongos (Query Route) servers
>   3. Start the mongod instances

#### Default ports
- mongos port 27017
- mongo config port 27019
- mongo replica port 27018

#### [Scalling out the cluster](docs/scale.md)

#### What must be done carefully

You must consider to backup the databases and understand how the database and log names are chosen by the script  

- Change the sharding order
  - The shards have numbered names, removing a shard must be done carefully as the shard names are used to locate the node database and logs
- Removing a shard
  - The shards have numbered names, removing a shard must be done carefully as the shard names are used to locate the node database and logs
  - If are doing this, it is advisable to delete or move the database files and logs of the removed shard
- Removing a node
  - It is advisable to remove or move the database files and logs of the removed node

####Managing by rest

- One benefit to wrapping the component in Ambari service is that you can now monitor/manage this service remotely via REST API

```bash
export SERVICE=MongoDB
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

#### Removing the service

- To remove the MongoDB:
  - Stop the service via Ambari
  - Delete the service

    ```bash
    curl -u admin:admin -i -H 'X-Requested-By: ambari' -X DELETE http://replace_with_your_ambari_hostname.com:8080/api/v1/clusters/ambari_cluster_name/services/MongoDB
    ```
  - Remove artifacts

    ```bash
    VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
    rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/mongo-ambari
    ```
  - Restart Ambari
    ```bash
    #sandbox
    service ambari restart

    #non sandbox
    sudo service ambari-server restart
    ```

#### Some configurations

![Image](docs/images/configs.png?raw=true)

#### Last Test Coverage Report

![Image](docs/images/tests.png?raw=true)

### References:

- This is a 99% rewritten version of the "geniuszhe" version: https://github.com/cas-bigdatalab/ambari-mongodb-cluster
