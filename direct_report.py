import sys
import argparse
import configparser
from datetime import date, datetime, timedelta
from pprint import pprint

import requests

parser = argparse.ArgumentParser(description="Generate PayPal reports using the PayPal REST API (direct integration version, no SDK)")
parser.add_argument('-m', '--server_mode', dest='mode', choices=('sandbox', 'live'), default='live')
parser.add_argument('-c', '--config_file', dest='config_filename', default='paypal_tools.conf', action="store")
parser.add_argument('-t', '--txn_id', dest='txn_id', action="store", required=True)

# set up environment: live (default) or sandbox (for testing)
mode = args.mode

# authentication and authorization
try:
  cfg = configparser.ConfigParser()
  cfg.read(args.config_filename)
except:
  sys.exit("Error reading configuration file args.config_filename")

base_url =  cfg[mode]['base_url']
client_id = cfg[mode]['client_id']
client_secret = cfg[mode]['client_secret']

endpoint = base_url + "/v1/reporting/transactions"

response = requests.post()





