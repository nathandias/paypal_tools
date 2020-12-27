import sys
import argparse
import configparser
from datetime import date, datetime, timedelta
from pprint import pprint

parser = argparse.ArgumentParser(description="Generate PayPal reports using the PayPal REST API")
parser.add_argument('-m', '--server_mode', dest='mode', choices=('sandbox', 'live'), default='live')
parser.add_argument('-c', '--config_file', dest='config_filename', default='paypal_tools.conf', action="store")
parser.add_argument('-s', '--start_date', dest='start_date', action='store', default=(date.today()-timedelta(days=30)).isoformat())
parser.add_argument('-e', '--end_date', dest='end_date', action='store', default=date.today().isoformat())
parser.add_argument('-r', "--report", dest='reports_to_run', action='append')

args = parser.parse_args()

try:
  cfg = configparser.ConfigParser()
  cfg.read(args.config_filename)
except:
  sys.exit("Error reading configuration file args.config_filename")

mode = args.mode
# Creating Access Token for Sandbox
client_id = cfg[mode]['client_id']
client_secret = cfg[mode]['client_secret']

import paypalrestsdk

paypalrestsdk.configure({
  'mode': mode,
  'client_id': client_id,
  'client_secret': client_secret })

# Fetch Payment
# payment = paypalrestsdk.Payment.find("PAY-57363176S1057143SKE2HO3A")

# Get List of Payments
# payment_history = paypalrestsdk.Payment.all({ "count" : 10 })

# from pprint import pprint

# for payment in payment_history.payments:
#     pprint(payment)

from paypalrestsdk.resource import List, Find, Create, Post, Update, Replace, Resource
from paypalrestsdk.api import default as default_api
import paypalrestsdk.util as util
from paypalrestsdk import exceptions

class Transaction(List, Find):
    """Transaction class wrapping the REST v1/transaction/transaction endpoint

    Usage::

        >>> transaction_history = Transaction.all({"count": 5})
        >>> transaction = Transaction.find("<TRANSACTION_ID>")

    """

    path = 'v1/reporting/transactions'

Transaction.convert_resources['transactions'] = Transaction
Transaction.convert_resources['transaction'] = Transaction

start_date = datetime.fromisoformat(args.start_date).isoformat(timespec="seconds")
end_date = datetime.fromisoformat(args.end_date).isoformat(timespec="seconds")

response = Transaction.all({
  'start_date' : start_date + '-0000',
  'end_date' : end_date + '-0000',
})

txn_dict = response.to_dict()

if args.reports_to_run:
  if 'with_notes' in args.reports_to_run:
    for txn in txn_dict['transaction_details']:
      info = txn['transaction_info']
      if ('transaction_note' in info):
          print(f"id:{info['transaction_id']} note:{info['transaction_note']}")









