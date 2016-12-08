#!/usr/bin/env bash

ps -aux | grep mongo | sed '/grep/D' | cut -f3 -d " " | xargs sudo kill -9
sudo rm -rf /var/lib/mongodb/node*
sudo rm -rf /var/log/mongodb/node*
sudo coverage run -m unittest discover . "*_test.py"
echo $0