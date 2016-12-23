#!/usr/bin/env bash

distros=(centos7)

for distro in ${distros[@]}; do
  docker run -it -v $(pwd):/app ambari-tests:$distro /app/package/test/runInstanceTests.sh
  result=$?

  if [[ $result != 0 ]]; then
    exit $result
  fi
done