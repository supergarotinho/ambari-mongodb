#!/usr/bin/env bash

rm -rf /var/lib/mongodb/node*
rm -rf /var/log/mongodb/node*
rm -f /app/package/test/coverage.xml

cd /app/package/test

coverage run -m unittest discover . "*_test.py"
result=$?

if [[ $result == 0 ]]; then
    coverage report
    coverage xml
    coveralls
fi

ps -aux | grep mongo | sed '/grep/D' | cut -f3 -d " " | xargs --no-run-if-empty kill -9

exit $result
