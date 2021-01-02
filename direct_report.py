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
args = parser.parse_args()

# set up environment: live (default) or sandbox (for testing)
mode = args.mode
print(f'Mode: {mode}')

# authentication and authorization
try:
  cfg = configparser.ConfigParser()
  cfg.read(args.config_filename)
except:
  sys.exit("Error reading configuration file args.config_filename")

base_url =  cfg[mode]['base_url']
client_id = cfg[mode]['client_id']
client_secret = cfg[mode]['client_secret']

def get_access_token(base_url, client_id, client_secret):

    print(f'Base URL: {base_url}')
    print(f'Client ID: {client_id}')
    print(f'Client Secret: {client_secret}')

    # get access token
    auth_endpoint = base_url + "/v1/oauth2/token"
    headers = {
        'Accept' : 'application/json',
        'Accept-Language' : 'en_US',
    }
    data = {
        'grant_type' : 'client_credentials'
    }

    response = requests.post(auth_endpoint, headers=headers, data=data, auth=(client_id, client_secret))

    if response.status_code != 200:
        sys.exit("Error: failed to get an access token / request returned something besides 200 OK")

    json_data = response.json()
    access_token = json_data['access_token']

    print("Authorization request response:")
    pprint(json_data)
    pprint(access_token)

    return access_token
}
transactions_endpoint = base_url + "/v1/reporting/transactions"
headers = {
    'Content-Type' : 'application/json',
    'Authorization' : f'Bearer {access_token}',
}

def api_query(base_url, endpoint, access_token, verb='get', url_params={}):
    
    headers = {
        'Content-Type' : 'application/json',
        'Authorization' : f'Bearer {access_token}',
    }

    query_url = base_url + endpoint + "?"

    f'{'


    if verb == 'get': 
        response = requests.get()



try:
    response = requests.get(transactions_endpoint, headers=headers)
    json_data = response.json()
    pprint(json_data)
except Exception as msg:
    sys.exit(msg)







