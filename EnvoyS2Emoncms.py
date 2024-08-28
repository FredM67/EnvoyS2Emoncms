#!/usr/bin/env python3

# This utility send a EnvoyS (Enphase) data to emoncms
#
# coded by:
# auteur : Frederic Metrich
# Email : Frederic.Metrich@Live.COM
version = "v3.00"

# if errors during executing this scrip make sure you installed phyton and the required modules/libraries
import configparser
import logging
import logging.handlers
import json
import urllib.request
import time
import ssl

DataJson_all  = { }

LogFile              = "/var/log/EnvoyS2Emoncms.log"
LogFileLastMessage   = "/tmp/EnvoyS2Emoncms.log"
WatchdogFile         = "/tmp/EnvoyS2Emoncms_Watchdog"

# Set logging params
def log_setup():
  log_handler = logging.handlers.WatchedFileHandler(LogFile)
  formatter = logging.Formatter('%(asctime)s PID(%(process)d) %(levelname)s: %(message)s')
  formatter.converter = time.gmtime  # if you want UTC time
  log_handler.setFormatter(formatter)
  logger = logging.getLogger()
  logger.addHandler(log_handler)
  logger.setLevel(logging.DEBUG)

###############################################################################################################
# Procedures
###############################################################################################################

log_setup()

logging.info("****** Starting EnvoyS2Emoncms.py ******")

Config = configparser.ConfigParser()
Config.read("/etc/Enphase/EnvoyS2Emoncms.cfg")

emon_privateKey = Config['emoncms']['privatekey']
emon_node_all   = Config['emoncms']['node_all']
emon_host       = Config['emoncms']['host']
emon_protocol   = Config['emoncms']['protocol']
emon_url        = Config['emoncms']['url']

envoy_url_all   = Config['envoy']['url_all']
envoy_host      = Config['envoy']['host']
envoy_protocol  = Config['envoy']['protocol']
envoy_token     = Config['envoy']['token']

logging.info('Configuration settings:')
logging.info('emoncms/privatekey: ' + emon_privateKey)
logging.info('emoncms/node_all: ' + emon_node_all)
logging.info('emoncms/host: ' + emon_host)
logging.info('emoncms/protocol: ' + emon_protocol)
logging.info('emoncms/url: ' + emon_url)

logging.info('envoy/url_all: ' + envoy_url_all)
logging.info('envoy/host: ' + envoy_host)
logging.info('envoy/protocol: ' + envoy_protocol)
logging.info('***********************')

###############################################################################################################
# Main program
###############################################################################################################

# Construct urls 
url_envoy_all  = envoy_protocol + envoy_host + envoy_url_all

myssl = ssl.create_default_context()
myssl.check_hostname=False
myssl.verify_mode=ssl.CERT_NONE

req = urllib.request.Request(url=url_envoy_all, method='GET')
req.add_header("Authorization", "Bearer " + envoy_token)
req.add_header("Accept", "application/json")

envoy_keys = ['wNow', 'whLifetime']

def ProceedData():
  try:
    # Fetch page with ENVOY detailed data
    the_page_all = urllib.request.urlopen(req, context = myssl).read()

    if len(the_page_all) < 4300:
      logging.warning("Page size: " + str(len(the_page_all)) + " \'" + str(the_page_all) + "\'")
    else:
      logging.info("Page size: " + str(len(the_page_all)))
  except ValueError as err:
    logging.error('Caught http exception: ' + str(err))
    logging.error('Received data: \'' + str(the_page_all) + '\'')
    return

  # Write raw output from envoy to file
  f1=open(LogFileLastMessage, "w")
  f1.write("INFO: page length(" + str(len(the_page_all)) + "): \'" + str(the_page_all) + "\'")
  f1.close()

  try:
    data_all = json.loads(the_page_all)
  except ValueError as err:
    logging.error('Caught json exception: ' + str(err))
    logging.error('Received data: \'' + str(the_page_all) + '\'')
    return

  DataJson_all.clear()

  # "measurementType": "production"
  DataJson_all['prod_' + 'whToday'] = data_all['production'][1]['whToday']
  for data in range(len(envoy_keys)):
    DataJson_all['prod_' + envoy_keys[data]] = data_all['production'][1][envoy_keys[data]]
  # for 3-phase details, comment out if you don't need it
  for phase in range(3):
    for data in range(len(envoy_keys)):
      DataJson_all['prod_L' + str(phase + 1) + '_' + envoy_keys[data]] = data_all['production'][1]['lines'][phase][envoy_keys[data]]

  # "measurementType": "total-consumption"
  DataJson_all['cons_' + 'whToday'] = data_all['consumption'][0]['whToday']
  for data in range(len(envoy_keys)):
    DataJson_all['cons_' + envoy_keys[data]] = data_all['consumption'][0][envoy_keys[data]]
  # for 3-phase details, comment out if you don't need it
  for phase in range(3):
    for data in range(len(envoy_keys)):
      DataJson_all['cons_L' + str(phase + 1) + '_' + envoy_keys[data]] = data_all['consumption'][0]['lines'][phase][envoy_keys[data]]

  # "measurementType": "net-consumption"
  # The next field is always zero, so skip it
  # DataJson_all['cons_' + 'whToday'] = data_all['consumption'][1]['whToday']
  for data in range(len(envoy_keys)):
    DataJson_all['net_' + envoy_keys[data]] = data_all['consumption'][1][envoy_keys[data]]
  # for 3-phase details, comment out if you don't need it
  for phase in range(3):
    for data in range(len(envoy_keys)):
      DataJson_all['net_L' + str(phase + 1) + '_' + envoy_keys[data]] = data_all['consumption'][1]['lines'][phase][envoy_keys[data]]

  url_all = emon_protocol + emon_host + emon_url + "time=" + str(data_all['production'][1]['readingTime']) + "&node=" + emon_node_all + "&apikey=" + emon_privateKey + "&fulljson=" + json.dumps(DataJson_all, separators=(',', ':'))

  HTTPresult_all = urllib.request.urlopen(url_all)
  if HTTPresult_all.getcode() == 200:
    logging.info("Response code : " +  str(HTTPresult_all.getcode()))
  else:
    logging.error("Response code : " +  str(HTTPresult_all.getcode()))
    logging.error("Original url was: '" + url_all + "'")

# Do forever ....
while True:
  try:
    time.sleep(5)

    # Write time to watchdog file, as a sign of life
    f3=open(WatchdogFile, "w")
    timestamp = int(time.time())
    f3.write (str(timestamp))
    f3.close()

    ProceedData()

  except Exception as e:
    logging.error('Caught exception: ' + str(e))
