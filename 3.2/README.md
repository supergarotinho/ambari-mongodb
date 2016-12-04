### An Ambari Stack for MongoDB Cluster 
Ambari stack for easily installing and managing MongoDB on HDP cluster,clusters include shard,replica,config,mongos.
http://www.bigdatalab.top/archives/180

####Feature
- auto install mongodb cluster ,include shard(replica set),config server,mongos server.
- support scale out ,add new shard 

![Image](../master/screenshots/cluster.png?raw=true)

###Assumptions

- Ambari is installed and running.
- No previous installations of Mongo DB exist. If there any, you can either remove it or rename it.
- have 3 nodes and more

Follow given step to install and manage Mongo DB using Ambari.

####Connect to the VM via SSH (password hadoop for sandbox image) and start Ambari server
```
ssh root@ambari.machine
```

####To deploy the Mongo DB, run below
```
on HDP 2.4
cd /var/lib/ambari-server/resources/stacks/HDP/2.4/services
git clone https://github.com/geniuszhe/ambari-mongodb-cluster.git
```

```sudo service ambari-server restart```


####Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:

On bottom left -> Actions -> Add service -> check MongoDB -> Next -> Next -> Next -> Deploy

![Image](../master/screenshots/addservice.png?raw=true)
![Image](../master/screenshots/assingnslave.png?raw=true)
![Image](../master/screenshots/customize.png?raw=true)
![Image](../master/screenshots/review.png?raw=true)

maybe there is something waring
![Image](../master/screenshots/warning.png?raw=true)
just restart the wrong  service
![Image](../master/screenshots/restart_warning.png?raw=true)


####On successful deployment you will see the MongoDB as part of Ambari stack and will be able to start/stop the service from here:

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
https://github.com/abajwa-hw/ntpd-stack




    
