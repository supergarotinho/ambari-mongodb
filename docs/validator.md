### Main Validator features

#### General Features

- Check in some of configured directories are the root dir 
- Check in some of configured directories they have special chars
- Check if the user deploying mongo config instances together with mongos instances in the same cluster

## Cluster configuration validations

- Check if all nodes in the cluster_configuration has the component installed on ambari
    - Also check if the user forget to mention some node fot that component
- Validate if port configuration leads to valid ports
- Check if the user specified, at least, the minimum number of needed ports for each component
- Check if we have more than one arbiter per shard
- Check if the shard has, at least, on non-arbiter node
- For configurations with more the one shard, detects if the user has also deployed mongo config and mongos servers in the cluster
- For sharding clusters:
  - Check if it have exactly 3 mongo config instances
  - Check if the user has configured any arbiter in the mongo config instances
  - Check if there is more than one arbiter per shard (it is not advisable)
