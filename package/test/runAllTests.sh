#!/usr/bin/env bash

distros=(centos7)

for distro in ${distros[@]}; do
  docker run -it -v /media/dados/Dropbox/Dados/Falometro/ambari/ambari-mongodb/:/app ambari-tests:centos7 /app/package/test/runInstanceTests.sh
  result=$?

  if [[ $result != 0 ]]; then
    exit $result
  fi
done