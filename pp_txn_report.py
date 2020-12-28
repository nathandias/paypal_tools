from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment, LiveEnvironment
from paypalhttp import HttpError
import sys
import argparse
import configparser
from datetime import date, datetime, timedelta
from pprint import pprint
from transactions.transactions_get_request import TransactionsGetRequest

# define and parse program arguments
parser = argparse.ArgumentParser(description="Generate PayPal reports using the PayPal REST API")
parser.add_argument('-m', '--server_mode', dest='mode', choices=('sandbox', 'live'), default='live')
parser.add_argument('-c', '--config_file', dest='config_filename', default='paypal_tools.conf', action="store")
parser.add_argument('-s', '--start_date', dest='start_date', action='store', default=(date.today()-timedelta(days=30)).isoformat())
parser.add_argument('-e', '--end_date', dest='end_date', action='store', default=date.today().isoformat())
parser.add_argument('-r', "--report", dest='reports_to_run', action='append')

args = parser.parse_args()

# read the default or override configuration file
try:
  cfg = configparser.ConfigParser()
  cfg.read(args.config_filename)
except:
  sys.exit("Error reading configuration file args.config_filename")

# Creating Access Token for Sandbox
mode = args.mode
client_id = cfg[mode]['client_id']
client_secret = cfg[mode]['client_secret']

# Creating an environment
if (mode == 'live'):
    environment = LiveEnvironment(client_id=client_id, client_secret=client_secret)
else:
    environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)

client = PayPalHttpClient(environment)

txn_id = '58T98774JE736684D'

request = TransactionsGetRequest(txn_id)

try:
    print("Environment:", mode)
    response = client.execute(request)
    
    print("Get transaction by id:", txn_id)
    print("Status code:", response.status_code)
    print("Full response object:")
    pprint(response)
except IOError as ioe:
    print(ioe)
    if isinstance(ioe, HttpError):
        # Something went wrong server-side
        print(ioe.status_code)
except:
    print("Whoops! Some sort of problem!")

