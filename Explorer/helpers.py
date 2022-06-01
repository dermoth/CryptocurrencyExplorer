import datetime
import decimal
import itertools
import json
import requests

id_counter = itertools.count()


def format_time(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


def average_age(timestamp, genesis_time):
    the_timestamp = datetime.datetime.fromtimestamp(timestamp)
    genesis_timestamp = datetime.datetime.fromtimestamp(genesis_time)
    difference = the_timestamp - genesis_timestamp
    difference_in_days = decimal.Decimal(difference.total_seconds()) / decimal.Decimal(86400)
    return f"{difference_in_days:.2f}"


def format_size(tx_size):
    return tx_size / 1000.0


class JSONRPC(object):
    def __init__(self, url, user, passwd, method=None, timeout=30):
        self.url = url
        self._user = user
        self._passwd = passwd
        self._method_name = method
        self._timeout = timeout

    def __getattr__(self, method_name):
        return JSONRPC(self.url, self._user, self._passwd, method_name, timeout=self._timeout)

    def __call__(self, *args):
        # rpc json call
        payload = json.dumps({'jsonrpc': '2.0', 'id': next(id_counter), "method": self._method_name, "params": args})
        headers = {'Content-type': 'application/json'}
        resp = None
        try:
            resp = requests.post(self.url, headers=headers, data=payload, timeout=self._timeout,
                                 auth=(self._user, self._passwd))
            resp = resp.json(parse_float=decimal.Decimal)
        except Exception:
            return

        if resp.get('error') is not None:
            raise JSONRPCException(resp['error'])
        elif 'result' not in resp:
            raise JSONRPCException({'code': -343, 'message': 'missing JSON-RPC result'})
        else:
            return resp['result']


class JSONRPCException(Exception):
    def __init__(self, rpc_error):
        parent_args = []
        try:
            parent_args.append(rpc_error['message'])
        except:
            pass
        Exception.__init__(self, *parent_args)
        self.error = rpc_error
        self.code = rpc_error['code'] if 'code' in rpc_error else None
        self.message = rpc_error['message'] if 'message' in rpc_error else None

    def __str__(self):
        return '%d: %s' % (self.code, self.message)

    def __repr__(self):
        return '<%s \'%s\'>' % (self.__class__.__name__, self)
