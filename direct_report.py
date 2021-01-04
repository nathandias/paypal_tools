import sys
import argparse
import configparser
from datetime import date, datetime, timedelta
from pprint import pprint

import requests
import pandas as pd

parser = argparse.ArgumentParser(description="Generate PayPal reports using the PayPal REST API (direct integration version, no SDK)")
parser.add_argument('-m', '--server_mode', dest='mode', choices=('sandbox', 'live'), default='live')
parser.add_argument('-c', '--config_file', dest='config_filename', default='paypal_tools.conf', action="store")
parser.add_argument('-t', '--txn_id', dest='txn_id', action="store")
parser.add_argument('-s', '--start_date', dest='start_date', action="store")
parser.add_argument('-e', '--end_date', dest='end_date', action="store")
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

def get_transactions(start_date, end_date):
    """
    Get all transactions in a specified date range
    """

    transactions = []

    while start_date <= end_date:
        if (end_date - start_date) <= timedelta(days=31):
            # this is the final set of transactions to collect, so break
            transactions += get_paged_transactions(start_date, end_date)
            break
        else:
            start_plus_31 = start_date + timedelta(days=31)
            transactions += get_paged_transactions(start_date, start_plus_31)
            start_date = start_plus_31
    else:
        sys.exit("in get_transactions: start_date ({start_date}) > end_date ({end_date})")
    
    return transactions

def get_paged_transactions(start_date, end_date):

    # expecting start_date <= end_date and, end_date - start_date <= 31

    print(f'"*** Getting transaction pages for date range start_date = {start_date} to end_date = {end_date} ***')

    global base_url, access_headers
    endpoint = base_url + "/v1/reporting/transactions?"

    parameters = {
        'start_date' : start_date.strftime("%Y-%m-%dT%H:%M:%S-0000"),
        'end_date' : end_date.strftime("%Y-%m-%dT%H:%M:%S-0000"),
        'page_size' : 500,
        'balance_affecting_records_only' : 'Y',
    }

    endpoint += '&'.join(f'{i[0]}={i[1]}' for i in parameters.items()) # join the url parameters

    page = 1
    transactions = []

    query_url = endpoint + f'&page={page}'

    response = requests.get(query_url, headers=access_headers)
    results = response.json()
    total_pages = results['total_pages']

    #print("Results page", page, "of", total_pages)
    #pprint(results)
    transactions += results['transaction_details']

    while (page < total_pages):
        page += 1
        query_url = endpoint + f'&page={page}'
        response = requests.get(query_url, headers=access_headers)
        results = response.json()
        #print("Results page", page, "of", total_pages)
        #pprint(results)
        transactions += results['transaction_details']

    # print("Number of transactions:", len(pages))
    # pprint(pages)
    
    return transactions

if (args.txn_id is not None): 
    capture_result = get_capture_details(args.txn_id)
    start_date = end_date = capture_result['create_time']
    transaction_result = get_full_transaction_details(args.txn_id, start_date, end_date)
    transactions = [transaction_result]

elif (args.start_date is not None) and (args.end_date is not None):
    start_date = datetime.strptime(args.start_date, "%Y-%m-%dT%H:%M:%S")
    end_date = datetime.strptime(args.end_date, "%Y-%m-%dT%H:%M:%S")
    if start_date > end_date:
        sys.exit(f'start_date ({start_date}) is after end_date ({end_date})')

    transactions = get_transactions(start_date, end_date)

else: # return last 31 days of transactions, the default if no command line options specified
    end_date = datetime.today()
    start_date = end_date - timedelta(days=31)
    transactions = get_transactions(start_date, end_date)

if transactions is not None:
    unpacked_t = [t['transaction_info'] for t in transactions]
    df = pd.DataFrame(unpacked_t)
    pprint(df)



