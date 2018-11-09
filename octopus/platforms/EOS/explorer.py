from octopus.engine.explorer import Explorer
from requests.exceptions import ConnectionError as RequestsConnectionError
import json

EOS_DEFAULT_RPC_PORT = 8888
EOS_WALLET_RPC_PORT = 8889


class EosExplorer(Explorer):
    """
    EOS REST RPC client class


    doc: https://eosio.github.io/eos/group__eosiorpc.html
    cleos source code: https://github.com/EOSIO/eos/blob/master/programs/cleos/main.cpp
    """
    def __init__(self, host='localhost', port=EOS_DEFAULT_RPC_PORT, tls=False, max_retries=3):
        Explorer.__init__(self, host=host, port=port, tls=tls, max_retries=max_retries)

    def call(self, method, params={}, version='v1', api_type='chain'):

        current_url = '{}/{}/{}/{}'.format(self.url, version, api_type, method)

        try:
            r = self.session.post(current_url, headers=self.headers, data=json.dumps(params))
        except RequestsConnectionError:
            raise Exception('RPC connection Error')
        if not 200 <= r.status_code < 300:
            raise Exception('RPC connection failure: ' + str(r.status_code) + ' ' + r.reason + ' ' + r.text)
        try:
            response = r.json()
        except ValueError:
            raise Exception('JSON response parsing error: ' + str(r.text))
        try:
            return response
        except KeyError:
            raise Exception('\"result\" field in JSON response error: ' + str(response))

    ##########################
    #        Chain API       #
    ##########################

    def get_info(self):
        '''Get latest information related to a node

        TESTED
        '''
        return self.call('get_info')

    def get_block(self, block_num_or_id):
        '''Get information related to a block.

        TESTED
        '''
        data = {'block_num_or_id': block_num_or_id}
        return self.call('get_block', data)

    def get_raw_code_and_abi(self, account_name):
        '''Fetch smart contract code.

        TESTED
        '''
        data = {'account_name': account_name}
        return self.call('get_raw_code_and_abi', data)

    def get_account(self, account_name):
        '''Get information related to an account.

        TESTED
        '''
        data = {'account_name': account_name}
        return self.call('get_account', data)

    def get_code(self, account_name):
        '''Fetch smart contract code.

        TESTED
        '''
        data = {'account_name': account_name}
        return self.call('get_code', data)

    def get_table_rows(self, scope, code, table, json=False, lower_bound=None, upper_bound=None, limit=None):
        '''Fetch smart contract data from an account.

        NOT TESTED
        '''
        data = {'scope': scope,
                'code': code,
                'table': table,
                'json': json}
        if lower_bound:
            data['lower_bound'] = lower_bound
        if upper_bound:
            data['upper_bound'] = upper_bound
        if limit:
            data['limit'] = limit
        return self.call('get_table_rows', data)

    def abi_json_to_bin(self, code, action, args):
        '''Serialize json to binary hex. The resulting binary hex is usually used for the data field in push_transaction.

        NOT TESTED
        '''
        data = {'code': code,
                'action': action,
                'args': args}
        print(data)
        return self.call('abi_json_to_bin', data)

    def abi_bin_to_json(self, code, action, binargs):
        '''Serialize back binary hex to json.

        NOT TESTED
        '''
        data = {'code': code,
                'action': action,
                'binargs': binargs}
        return self.call('abi_bin_to_json', data)

    def push_transaction(self, tx_json):
        '''This method expects a transaction in JSON format and will attempt to apply it to the blockchain,

        NOT TESTED
        '''
        return self.call('push_transaction', tx_json)

    def push_transactions(self, list_tx_json):
        '''This method push multiple transactions at once.

        NOT TESTED
        '''
        return self.call('push_transactions', list_tx_json)

    def get_required_keys(self, transaction):
        '''Get required keys to sign a transaction from list of your keys.

        NOT TESTED
        '''
        data = {'transaction': transaction}
        return self.call('get_required_keys', data)

    ##########################
    #       Wallet API       #
    ##########################

    def wallet_create(self, name):
        '''Create a new wallet with the given name

        TESTED
        '''
        return self.call('create', name, api_type='wallet')

    def wallet_open(self, name):
        '''Open an existing wallet of the given name

        TESTED
        '''
        return self.call('open', name, api_type='wallet')

    def wallet_lock(self, name):
        '''Lock a wallet of the given name

        TESTED
        '''
        return self.call('lock', name, api_type='wallet')

    def wallet_lock_all(self):
        '''Lock all wallets

        TESTED
        '''
        return self.call('lock_all', api_type='wallet')

    def wallet_unlock(self, name, password):
        '''Unlock a wallet with the given name and password

        TESTED
        '''
        return self.call('unlock', [name, password], api_type='wallet')

    def wallet_import_key(self, name, priv_key):
        '''Import a private key to the wallet of the given name

        TESTED
        '''
        return self.call('import_key', [name, priv_key], api_type='wallet')

    def wallet_list(self):
        '''List all wallets

        TESTED
        '''
        return self.call('list_wallets', api_type='wallet')

    def wallet_list_keys(self):
        '''List all key pairs across all wallets

        TESTED
        '''
        return self.call('list_keys', api_type='wallet')

    def wallet_get_public_keys(self):
        '''List all public keys across all wallets

        TESTED
        '''
        return self.call('get_public_keys', api_type='wallet')

    def wallet_set_timeout(self, timeout_s):
        '''Set wallet auto lock timeout (in seconds)

        TESTED
        '''
        return self.call('set_timeout', timeout_s, api_type='wallet')

    def wallet_sign_trx(self, tx_json):
        '''Sign transaction given an array of transaction, require public keys, and chain id

        NOT TESTED
        '''
        return self.call('sign_transaction', tx_json)
