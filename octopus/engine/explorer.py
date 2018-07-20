import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError as RequestsConnectionError

import json


class Explorer(object):
    '''
    Generic JSON-RPC client class
    '''

    def __init__(self, host='localhost', port=8332, tls=False, max_retries=3):
        self.host = host
        self.port = port
        self.tls = tls
        self.session = requests.Session()
        self.session.mount(self.host, HTTPAdapter(max_retries=max_retries))
        self.headers = {'Content-Type': 'application/json'}

        self.scheme = 'https' if self.tls else 'http'

        self.url = '{}://{}:{}'.format(self.scheme, self.host, self.port)

    def call(self, method, params=None, jsonrpc=None, _id=None):

        params = params or []
        jsonrpc = jsonrpc or '2.0'
        data = {
            'jsonrpc': jsonrpc,
            'method': method,
            'params': params,
        }
        if _id is not None:
            data['id'] = _id

        try:
            r = self.session.post(self.url, headers=self.headers, data=json.dumps(data))
        except RequestsConnectionError:
            raise Exception('RPC connection Error')
        if not 200 <= r.status_code < 300:
            raise Exception('RPC connection failure: ' + str(r.status_code) + ' ' + r.reason)
        try:
            response = r.json()
        except ValueError:
            raise Exception('JSON response parsing error: ' + str(r.text))
        try:
            return response['result']
        except KeyError:
            raise Exception('\"result\" field in JSON response error: ' + str(response))

    #######################
    # HIGHT-LEVEL METHODS #
    #######################

    def get_transaction(self, transaction_id, verbosity):
        '''
        return transaction informations

        ex :
            binding of eth_getTransactionByHash() for Ethereum
            binding of getrawtransaction() for Bitcoin
            binding of getrawtransaction() for Neo
        '''
        return NotImplementedError

    def get_block_by_number(self, block_number):
        '''
        return block information using given block number

        ex :
            binding of eth_getBlockByNumber() for Ethereum
            binding of getblockhash() + getblock() for Bitcoin
            binding of getblock() for Neo
        '''
        return NotImplementedError

    def get_block_by_hash(self, block_hash):
        '''
        return block information using given block hash

        ex :
            binding of eth_getBlockByHash() for Ethereum
            binding of getblock() for Bitcoin
            binding of getblock() for Neo
        '''
        return NotImplementedError

    def decode_tx(txid):
        '''
        return dict with important transaction information
        '''
        return NotImplementedError
