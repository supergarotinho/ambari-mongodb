<h1 align="center">An Ambari Stack for MongoDB Cluster &nbsp; <a href="https://twitter.com/intent/tweet?text=Deploy%2C%20configure%20and%20monitor%20MongoDB%20cluster%20with%20Apache%20Ambari%20and%20supergarotinho%2Fambari-mongodb%20!&amp;url=https://www.gruponeuro.com.br&amp;via=supergarotinho&amp;hashtags=ambari,bigdata,big-data,hdp,hortonworks,mongodb,mongo,data" rel="nofollow"><img src="https://camo.githubusercontent.com/83d4084f7b71558e33b08844da5c773a8657e271/68747470733a2f2f696d672e736869656c64732e696f2f747769747465722f75726c2f687474702f736869656c64732e696f2e7376673f7374796c653d736f6369616c" alt="Tweet" data-canonical-src="https://img.shields.io/twitter/url/http/shields.io.svg?style=social" style="max-width:100%;"></a>
</h1>
<div align="center">
  Ambari stack for easily installing and managing MongoDB on HDP cluster with any kind of cluster architecture.
</div>

<br />

<div align="center">

  <!-- Build Status -->
  <a href="https://travis-ci.org/supergarotinho/ambari-mongodb">
    <img src="https://travis-ci.org/supergarotinho/ambari-mongodb.svg?branch=master"
      alt="Build Status" />
  </a>
  <!-- Coverage Status -->
  <a href="https://coveralls.io/github/supergarotinho/ambari-mongodb?branch=master">
    <img src="https://coveralls.io/repos/github/supergarotinho/ambari-mongodb/badge.svg?branch=master" />
  </a>
  <!-- Price -->
  <a href="https://github.com/supergarotinho/bashtest-example/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/price-FREE-0098f7.svg"
      alt="Price" />
  </a>
  <!-- License: BSD-3 -->
  <a href="https://github.com/supergarotinho/bashtest-example/blob/master/LICENSE">
    <img src="https://img.shields.io/badge/license-BSD3-blue.svg"
      alt="License: BSD-3" />
  </a>
  <!-- Contributions welcome -->
  <img src="https://img.shields.io/badge/contributions-welcome-orange.svg"
    alt="Contributions welcome" />
</div>

<br/>

<div align="center">
  <strong>Author:</strong> <a href="https://br.linkedin.com/in/andersonrss">Anderson Santos</a>
</div>

<div align="center">
  <sub>Built with ❤︎ by
  <a href="https://br.linkedin.com/in/andersonrss">Anderson Santos</a> and
  <a href="https://github.com/supergarotinho/bashtest-example/graphs/contributors">
    contributors
  </a>
</div>

## Table of contents

- [Features](#features)
  - [Some configurations](#some-configurations)
  - [Features in development stage](#features-in-development-stage)
  - [Future Features and development](#future-features-and-development)
- [MongoDB Replicaset Cluster Architecture](#mongodb-replicaset-cluster-architecture)
- [MongoDB Sharding Cluster Architecture](#mongodb-sharding-cluster-architecture)
- [Assumptions](#assumptions)
- [Getting Started](#getting-started)
  - [Setup](#setup)
  - [Default ports](#default-ports)
  - [What must be done carefully](#what-must-be-done-carefully)
  - [Managing by rest](#managing-by-rest)
- [Removing the service](#removing-the-service)
- [Running the tests](#running-the-tests)
  - [Last Test Coverage Report](#last-test-coverage-report)
- [Authors](#authors)
- [License](#license)
- [Acknowledgments](#acknowledgments)

## Features

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
  - Configure which instances will be in which shard
  - Configure which instances will act as an arbiter
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
- **Testing**
  - An test wrapper that execute integrated tests at various linux distros using docker 
  - An docker instance to setup an testing environment and execute the integrated tests for CentOS 7 distro
- **Well documented and tested**

### Some configurations

![Image](docs/images/configs.png?raw=true)

### Features in development stage

- Add logOpSize config option 
- An alert when the cluster is up but the shards are not 100% ok
  - If there are missing nodes on it
- An alert when the shards are not in the mongos (Query Router) shard list
- An command to re-configure the cluster:
  - Adding the missing nodes to the shard
  - Adding the missing shards to the mongos list

### Future Features and development

We are needing help for these features. We have already developed some draft scripts and solutions for it.

- **Testing**
  - The tests for the service_advisor script
- Few modifications to support other linux distros (including testing)
- **A metrics monitor** to send several metrics from the mongo instances to ambari
  - And the ambari metrics screen :)
- **Useful Tasks:**  
  - A command to delete nodes and shards
  - A command to change the shard order
  - A command to backup the databases
  - A command to restore the databases

## MongoDB Replicaset Cluster Architecture 

![Image](docs/images/mongodb-repl-cluster.png?raw=true)

## MongoDB Sharding Cluster Architecture 

![Image](docs/images/mongodb-shard-cluster.png?raw=true)

## Assumptions

- Ambari is installed and running.
- No previous installations of Mongo DB exist. If there any, you can either remove it or rename it.

## Getting Started

### Setup

Follow given step to install and manage Mongo DB using Ambari.

1. Connect to the VM via SSH (password hadoop for sandbox image) and start Ambari server 

  ```bash
  ssh root@ambari.machine
  ```
  
2. To deploy the Mongo DB, run below 

  ```bash
  VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
  sudo git clone https://github.com/supergarotinho/ambari-mongodb /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/MongoDB
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

### Default ports
- mongos port 27017
- mongo config port 27019
- mongo replica port 27018

### What must be done carefully

You must consider to backup the databases and understand how the database and log names are chosen by the script  

- Change the sharding order
  - The shards have numbered names, removing a shard must be done carefully as the shard names are used to locate the node database and logs
- Removing a shard
  - The shards have numbered names, removing a shard must be done carefully as the shard names are used to locate the node database and logs
  - If are doing this, it is advisable to delete or move the database files and logs of the removed shard
- Removing a node
  - It is advisable to remove or move the database files and logs of the removed node

### Managing by rest

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

## Removing the service

- To remove the MongoDB:
  - Stop the service via Ambari
  - Delete the service

    ```bash
    curl -u admin:admin -i -H 'X-Requested-By: ambari' -X DELETE http://replace_with_your_ambari_hostname.com:8080/api/v1/clusters/ambari_cluster_name/services/MongoDB
    ```
  - Remove artifacts

    ```bash
    VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
    rm -rf /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/MongoDB
    ```
  - Restart Ambari
    ```bash
    #sandbox
    service ambari restart

    #non sandbox
    sudo service ambari-server restart
    ```


## Running the tests

```bash
package/test/runAllTests.sh
```

### Last Test Coverage Report

![Image](docs/images/tests.png?raw=true)

## Authors

* **Anderson Santos** - *Initial work* - [supergarotinho](https://github.com/supergarotinho)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the BSD-3 License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

- This is a 99% rewritten version of the "geniuszhe" version: https://github.com/cas-bigdatalab/ambari-mongodb-cluster
