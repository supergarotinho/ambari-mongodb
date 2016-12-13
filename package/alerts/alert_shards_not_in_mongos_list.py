#!/usr/bin/env python

import logging
import traceback

MONGODB_KEY = '{{mongodb}}'
MONGOD_KEY = '{{mongod}}'
MONGOCONF_KEY = '{{mongo-conf}}'
MONGOS_KEY = '{{mongos}}'

logger = logging.getLogger('ambari_alerts')

def get_tokens():
  """
  Returns a tuple of tokens in the format {{site/property}} that will be used
  to build the dictionary passed into execute

  :rtype tuple
  """
  return (MONGODB_KEY,MONGOD_KEY,MONGOCONF_KEY,MONGOCONF_KEY,MONGOS_KEY)

def execute(configurations={}, parameters={}, host_name=None):
  """
  Returns a tuple containing the result code and a pre-formatted result label
  Keyword arguments:
  configurations : a mapping of configuration key to value
  parameters : a mapping of script parameter key to value
  host_name : the name of this host where the alert is running
  :type configurations dict
  :type parameters dict
  :type host_name str

  :return (result_code, [label]) - result_code can be: CRITICAL, WARNING, UNKNOWN or OK
  """

  try:
    logger.info("Configurations: " + str(configurations))
    label = "This is a test!"
    result_code = 'WARNING'
  except:
    label = traceback.format_exc()
    result_code = 'UNKNOWN'

  return ((result_code,[label]))

if __name__ == '__main__':
  execute()