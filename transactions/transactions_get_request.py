import paypalhttp

try:
    from urllib import quote  # Python 2.X
except ImportError:
    from urllib.parse import quote  # Python 3+

class TransactionsGetRequest:
    """
    Shows details for a transaction, by id
    """
    def __init__(self, txn_id):
        # start_date = '2020-12-01T00:00:00-0000'
        # end_date = '2020-12-31T00:00:00-0000'
        self.verb = "GET"
        self.path = "/v1/reporting/transactions"
        # self.path += f'&start_date={quote(str(start_date))}'
        # self.path += f'&end_date={quote(str(end_date))}'
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = None

