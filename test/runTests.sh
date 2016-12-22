#!/usr/bin/env bash

ps -aux | grep mongo | sed '/grep/D' | cut -f3 -d " " | xargs kill -9
rm -rf /var/lib/mongodb/node*
rm -rf /var/log/mongodb/node*
coverage run -m unittest discover . "*_test.py"
echo $0