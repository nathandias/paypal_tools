import sys
import argparse
import configparser
from datetime import date, datetime, timedelta
from pprint import pprint

import requests

parser = argparse.ArgumentParser(description="Generate PayPal reports using the PayPal REST API (direct integration version, no SDK)")
parser.add_argument('-m', '--server_mode', dest='mode', choices=('sandbox', 'live'), default='live')
parser.add_argument('-c', '--config_file', dest='config_filename', default='paypal_tools.conf', action="store")
parser.add_argument('-t', '--txn_id', dest='txn_id', action="store")
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

access_token = get_access_token(base_url, client_id, client_secret)
access_headers = {
    'Content-Type' : 'application/json',
    'Authorization' : f'Bearer {access_token}'
}



def get_capture_details(txn_id):
    """
    Print and return the captured payment details as a json object.
    Uses the /v2/payments/captures endpoint which allows searching all
    available transaction history (without specifying start_date or end_date).
    Returned capture doesn't include "notes" and other transaction fields; to
    get these, follow up with a get_full_transaction_details call
    """

    print("*** Getting captured payment details for txn_id =", txn_id, "***")

    global base_url, access_headers
    endpoint = base_url + "/v2/payments/captures/" + txn_id
    
    try:
        response = requests.get(endpoint, headers=access_headers)
        json_data = response.json()
        pprint(json_data)
        return json_data
    except Exception as msg:
        sys.exit(msg)


def get_full_transaction_details(txn_id, start_date, end_date):

    print("*** Getting full transaction details for txn_id =", txn_id, "start_date =", start_date, "end_date =", end_date, "***")

    global base_url, access_headers
    endpoint = base_url + "/v1/reporting/transactions?"
    endpoint += f'transaction_id={txn_id}&start_date={start_date}&end_date={end_date}'

    try:
        response = requests.get(endpoint, headers=access_headers)
        json_data = response.json()
        pprint(json_data)
        return json_data
    except Exception as msg:
        sys.exit(msg)



if (args.txn_id is not None): 
    capture_result = get_capture_details(args.txn_id)
    start_date = end_date = capture_result['create_time']
    transaction_result = get_full_transaction_details(args.txn_id, start_date, end_date)



