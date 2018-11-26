import warnings

#from ethereum import utils
#from ethereum.abi import encode_abi, decode_abi

from octopus.platforms.ETH.constants import DEFAULT_GAS_PER_TX, DEFAULT_GAS_PRICE, BLOCK_TAGS, BLOCK_TAG_LATEST
from octopus.platforms.ETH.util import hex_to_dec, clean_hex, validate_block

from octopus.engine.explorer import Explorer
"""
This code is adapted from: ethjsonrpc
https://github.com/ConsenSys/ethjsonrpc
"""

GETH_DEFAULT_RPC_PORT = 8545
ETH_DEFAULT_RPC_PORT = 8545
PARITY_DEFAULT_RPC_PORT = 8545
PYETHAPP_DEFAULT_RPC_PORT = 4000

INFURA_MAINNET = "mainnet.infura.io/"
INFURA_ROPSTEN = "ropsten.infura.io/"
INFURA_INFURANET = "infuranet.infura.io/"
INFURA_KOVAN = "kovan.infura.io/"
INFURA_RINKEBY = "rinkeby.infura.io/"
INFURA_RPC_PORT = 8545

INFURA_APIKEY = "bHuaQhX91nkQBac8Wtgj"


class EthereumExplorerRPC(Explorer):
    """
    Ethereum JSON-RPC client class
    """
    def __init__(self, host='localhost', port=GETH_DEFAULT_RPC_PORT, tls=False, max_retries=3):
        Explorer.__init__(self, host=host, port=port, tls=tls, max_retries=max_retries)

    def call(self, method, params=None, jsonrpc='2.0', _id=1):
        return super().call(method, params, jsonrpc, _id)

    '''
    def _encode_function(self, signature, param_values):

        prefix = utils.big_endian_to_int(utils.sha3(signature)[:4])

        if signature.find('(') == -1:
            raise RuntimeError('Invalid function signature. Missing "(" and/or ")"...')

        if signature.find(')') - signature.find('(') == 1:
            return utils.encode_int(prefix)

        types = signature[signature.find('(') + 1: signature.find(')')].split(',')
        encoded_params = encode_abi(types, param_values)
        return utils.zpad(utils.encode_int(prefix), 4) + encoded_params
    '''

    #######################
    # HIGHT-LEVEL METHODS #
    #######################

    def get_transaction(self, transaction_id, verbosity=None):
        """ Return transaction informations

        .. seealso::
            :method:`eth_getTransactionByHash`
        """
        return self.eth_getTransactionByHash(transaction_id)

    def get_block_by_number(self, block_number):
        """ Return block information using given block number

        .. seealso::
            :method:`eth_getBlockByNumber`
        """
        return self.eth_getBlockByNumber(block_number)

    def get_block_by_hash(self, block_hash):
        """ Return block information using given block hash

        .. seealso::
            :method:`eth_getBlockByHash`
        """
        return self.eth_getBlockByHash(block_hash)

    def decode_tx(self, transaction_id):
        """ Return dict with important information about
            the given transaction
        """
        tx_data = self.eth_getTransactionByHash(transaction_id)
        return tx_data
        #TODO


    ##########################
    # HIGHT-LEVEL METHODS #2 #
    ##########################

    def transfer(self, from_address, to_address, amount):
        """Send wei from one address to another

        TODO

        .. note:: https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendtransaction
        .. seealso:: :method:`eth_sendTransaction`
        """
        return self.eth_sendTransaction(from_address=from_address, to_address=to_address, value=amount)

    def create_contract(self, from_, code, gas, sig=None, args=None):
        """
        Create a contract on the blockchain from compiled EVM code. Returns the
        transaction hash.
        """
        '''
        from_ = from_ or self.eth_coinbase()
        if sig is not None and args is not None:
            types = sig[sig.find('(') + 1: sig.find(')')].split(',')
            encoded_params = encode_abi(types, args)
            code += encoded_params.encode('hex')
        return self.eth_sendTransaction(from_address=from_, gas=gas, data=code)
        '''
        return NotImplementedError()

    def get_contract_address(self, tx):
        """
        Get the address for a contract from the transaction that created it
        """
        receipt = self.eth_getTransactionReceipt(tx)
        return receipt['contractAddress']

    def call_without_transaction(self, address, sig, args, result_types):
        """
        Call a contract function on the RPC server, without sending a
        transaction (useful for reading data)
        """
        '''
        data = self._encode_function(sig, args)
        data_hex = data.encode('hex')
        response = self.eth_call(to_address=address, data=data_hex)
        return decode_abi(result_types, response[2:].decode('hex'))
        '''
        return NotImplementedError()

    def call_with_transaction(self, from_, address, sig, args, gas=None, gas_price=None, value=None):
        """
        Call a contract function by sending a transaction (useful for storing
        data)
        """
        '''
        gas = gas or DEFAULT_GAS_PER_TX
        gas_price = gas_price or DEFAULT_GAS_PRICE
        data = self._encode_function(sig, args)
        data_hex = data.encode('hex')
        return self.eth_sendTransaction(from_address=from_, to_address=address, data=data_hex, gas=gas,
                                        gas_price=gas_price, value=value)
        '''
        return NotImplementedError()

    ####################
    # JSON-RPC METHODS #
    ####################

    # ressources :
    # * https://github.com/ethereum/wiki/wiki/JSON-RPC
    # *
    # *

    def web3_clientVersion(self):
        """ Returns the current client version.

        :return: The current client version
        :rtype: str

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.web3_clientVersion()
        'Geth/v1.8.0-unstable-952482d5/linux-amd64/go1.9.2'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#web3_clientversion
        .. todo::
            TESTED
        """

        return self.call('web3_clientVersion')

    def web3_sha3(self, data):
        """ Returns Keccak-256 (not the standardized SHA3-256) of the given data.

        :param data: the data to convert into a SHA3 hash
        :type data: hex string
        :return: The SHA3 result of the given string.
        :rtype: hex string

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.web3_sha3('0x' + b'hello world'.hex())
        '0x47173285a8d7341e5e972fc677286384f802f8ef42a5ec5f03bbfa254cb01fad'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#web3_sha3
        .. todo::
            TESTED
        """
        #data = str(data).encode('hex')
        return self.call('web3_sha3', [data])

    def net_version(self):
        """ Returns the current network id.

        :return: The current network id.
            "1": Ethereum Mainnet
            "2": Morden Testnet (deprecated)
            "3": Ropsten Testnet
            "4": Rinkeby Testnet
            "42": Kovan Testnet
        :rtype: str

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.net_version()
        '1'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#net_version
        .. todo::
            TESTED
        """
        return self.call('net_version')

    def net_listening(self):
        """ Returns true if client is actively listening for network connections.

        :return: The current network id.
            true when listening otherwise false.
        :rtype: Boolean

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.net_listening()
        True


        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#net_listening
        .. todo::
            TESTED
        """
        return self.call('net_listening')

    def net_peerCount(self):
        """ Returns number of peers currently connected to the client.

        :return: integer of the number of connected peers.
        :rtype: int

        :Example:
        >>> explorer = EthereumExplorerRPC()
        >>> explorer.net_peerCount()
        25

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#net_peercount
        .. todo::
            TESTED
        """
        return hex_to_dec(self.call('net_peerCount'))

    def eth_protocolVersion(self):
        """ Returns the current ethereum protocol version.

        :return: The current ethereum protocol version
        :rtype: hex str

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_protocolVersion()
        '0x3f'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_protocolversion
        .. todo::
            TESTED
        """
        return self.call('eth_protocolVersion')

    def eth_syncing(self):
        """ Returns an object with data about the sync status or false.

        :return: An object with sync status data or FALSE, when not syncing
            startingBlock: QUANTITY - The block at which the import started (will only be reset, after the sync reached his head)
            currentBlock: QUANTITY - The current block, same as eth_blockNumber
            highestBlock: QUANTITY - The estimated highest block
        :rtype: Boolean or object

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_syncing()
        False

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_syncing
        .. todo::
            TESTED
        """
        return self.call('eth_syncing')

    def eth_coinbase(self):
        """ Returns the client coinbase address.

        :return: 20 bytes - the current coinbase address.
        :rtype: hex str

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_coinbase()
        '0x407d73d8a49eeb85d32cf465507dd71d507100c1'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_coinbase
        .. todo::
            TESTED
        """
        return self.call('eth_coinbase')

    def eth_mining(self):
        """ Returns true if client is actively mining new blocks.

        :return:  returns true of the client is mining, otherwise false
        :rtype: Boolean

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_mining()
        False

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_mining
        .. todo::
            TESTED
        """
        return self.call('eth_mining')

    def eth_hashrate(self):
        """ Returns the number of hashes per second that the node is mining with.

        :return: number of hashes per second.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_hashrate()
        0

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_hashrate
        .. todo::
            TESTED
        """

        return hex_to_dec(self.call('eth_hashrate'))

    def eth_gasPrice(self):
        """ Returns the current price per gas in wei.

        :return: integer of the current gas price in wei.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_gasPrice()
        4000000000

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gasprice
        .. todo::
            TESTED
        """
        return hex_to_dec(self.call('eth_gasPrice'))

    def eth_accounts(self):
        """ Returns a list of addresses owned by client.

        :return: 20 Bytes - addresses owned by the client.
        :rtype: list

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_accounts()
        ["0x407d73d8a49eeb85d32cf465507dd71d507100c1"]

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_accounts
        .. todo::
            TESTED
        """
        return self.call('eth_accounts')

    def eth_blockNumber(self):
        """ Returns the number of most recent block.

        :return: integer of the current block number the client is on.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_blockNumber()
        5100196

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_blocknumber
        .. todo::
            TESTED
        """
        return hex_to_dec(self.call('eth_blockNumber'))

    def eth_getBalance(self, address=None, block=BLOCK_TAG_LATEST):
        """ Returns the balance of the account of given address.

        :param address: 20 Bytes - address to check for balance.
        :type address: str
        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :return:  integer of the current balance in wei.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getBalance("0x956b6B7454884b734B29A8115F045a95179ea00C")
        17410594678300000000

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getbalance
        .. todo::
            TESTED

        """
        address = address or self.eth_coinbase()
        block = validate_block(block)
        v = hex_to_dec(self.call('eth_getBalance', [address, block]))
        return (v if v else 0)

    def eth_getStorageAt(self, address=None, position=0, block=BLOCK_TAG_LATEST):
        """ Returns the value from a storage position at a given address.

        :param address: 20 Bytes - address to check for balance.
        :type address: str
        :param address: (optionnal) integer of the position in the storage. default is 0
        :type address: int
        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :return:  the value at this storage position.
        :rtype: str

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getStorageAt("0x295a70b2de5e3953354a6a8344e616ed314d7251", 0, "latest")
        '0x0000000000000000000000000000000000000000000000000000000000000000'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getstorageat
        .. todo::
            TESTED
        """
        block = validate_block(block)
        return self.call('eth_getStorageAt', [address, hex(position), block])

    def eth_getTransactionCount(self, address, block=BLOCK_TAG_LATEST):
        """ Returns the number of transactions sent from an address.

        :param address: 20 Bytes - address.
        :type address: str
        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :return: integer of the number of transactions send from this address.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getTransactionCount("0x956b6B7454884b734B29A8115F045a95179ea00C")
        12891

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactioncount
        .. todo::
            TESTED
        """
        block = validate_block(block)
        return hex_to_dec(self.call('eth_getTransactionCount', [address, block]))

    def eth_getBlockTransactionCountByHash(self, block_hash):
        """ Returns the number of transactions in a block from a block matching the given block hash.

        :param block_hash:  32 Bytes - hash of a block
        :type block_hash: str
        :return: integer of the number of transactions in this block.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getBlockTransactionCountByHash('0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b')
        69

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblocktransactioncountbyhash
        .. todo::
            TESTED
        """
        return hex_to_dec(self.call('eth_getBlockTransactionCountByHash', [block_hash]))

    def eth_getBlockTransactionCountByNumber(self, block=BLOCK_TAG_LATEST):
        """ Returns the number of transactions in a block matching the given block number.

        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :return:  integer of the number of transactions in this block.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getBlockTransactionCountByNumber(5100196)
        69

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblocktransactioncountbynumber
        .. todo::
            TESTED
        """
        block = validate_block(block)
        return hex_to_dec(self.call('eth_getBlockTransactionCountByNumber', [block]))

    def eth_getUncleCountByBlockHash(self, block_hash):
        """ Returns the number of transactions in a block matching the given block number.

        :param block_hash: 32 Bytes - hash of a block
        :type block_hash: str
        :return: integer of the number of uncles in this block.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getUncleCountByBlockHash('0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b')
        0


        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclecountbyblockhash
        .. todo::
            TESTED
        """
        return hex_to_dec(self.call('eth_getUncleCountByBlockHash', [block_hash]))

    def eth_getUncleCountByBlockNumber(self, block=BLOCK_TAG_LATEST):
        """ Returns the number of uncles in a block from a block matching the given block number.

        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :return: integer of the number of uncles in this block.
        :rtype: int

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getUncleCountByBlockNumber(5100196)
        0

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclecountbyblocknumber
        .. todo::
            TESTED
        """
        block = validate_block(block)
        return hex_to_dec(self.call('eth_getUncleCountByBlockNumber', [block]))

    def eth_getCode(self, address, default_block=BLOCK_TAG_LATEST):
        """ Returns code at a given address.

        :param address: 20 Bytes - address.
        :type address: str
        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :return: the code from the given address.
        :rtype: hex str

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getCode("0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413")
        '0x6060604052361561020e5760e060020a6000350463013cf08b[...]62f93160ef3e563'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcode
        .. todo::
            TESTED
        """
        default_block = validate_block(default_block)
        return self.call('eth_getCode', [address, default_block])

    def eth_sign(self, address, data):
        """ The sign method calculates an Ethereum specific signature with: sign(keccak256("\x19Ethereum Signed Message:\n" + len(message) + message))).

        By adding a prefix to the message makes the calculated signature recognisable as an Ethereum specific signature.
        This prevents misuse where a malicious DApp can sign arbitrary data (e.g. transaction) and use the signature to impersonate the victim.

        :param address: 20 Bytes - address.
        :type address: str
        :param data: N Bytes - message to sign
        :type data: hex str
        :return: Signature
        :rtype: hex str

        .. note::
            the address to sign with must be unlocked.
        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sign
        .. todo::
            NOT TESTED
        """
        return self.call('eth_sign', [address, data])

    def eth_sendTransaction(self, to_address=None, from_address=None, gas=None, gas_price=None, value=None, data=None,
                            nonce=None):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendtransaction

        NEEDS TESTING
        """
        params = {}
        params['from'] = from_address or self.eth_coinbase()
        if to_address is not None:
            params['to'] = to_address
        if gas is not None:
            params['gas'] = hex(gas)
        if gas_price is not None:
            params['gasPrice'] = clean_hex(gas_price)
        if value is not None:
            params['value'] = clean_hex(value)
        if data is not None:
            params['data'] = data
        if nonce is not None:
            params['nonce'] = hex(nonce)
        return self.call('eth_sendTransaction', [params])

    def eth_sendRawTransaction(self, data):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_sendrawtransaction

        NEEDS TESTING
        """
        return self.call('eth_sendRawTransaction', [data])

    def eth_call(self, to_address, from_address=None, gas=None, gas_price=None, value=None, data=None,
                 default_block=BLOCK_TAG_LATEST):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_call

        NEEDS TESTING
        """
        default_block = validate_block(default_block)
        obj = {}
        obj['to'] = to_address
        if from_address is not None:
            obj['from'] = from_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = clean_hex(gas_price)
        if value is not None:
            obj['value'] = value
        if data is not None:
            obj['data'] = data
        return self.call('eth_call', [obj, default_block])

    def eth_estimateGas(self, to_address=None, from_address=None, gas=None, gas_price=None, value=None, data=None,
                        default_block=BLOCK_TAG_LATEST):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_estimategas

        NEEDS TESTING
        """
        if isinstance(default_block, basestring):
            if default_block not in BLOCK_TAGS:
                raise ValueError
        obj = {}
        if to_address is not None:
            obj['to'] = to_address
        if from_address is not None:
            obj['from'] = from_address
        if gas is not None:
            obj['gas'] = hex(gas)
        if gas_price is not None:
            obj['gasPrice'] = clean_hex(gas_price)
        if value is not None:
            obj['value'] = value
        if data is not None:
            obj['data'] = data
        return hex_to_dec(self.call('eth_estimateGas', [obj, default_block]))

    def eth_getBlockByHash(self, block_hash, tx_objects=True):
        """ Returns information about a block by hash.

        :param block_hash: 32 Bytes - Hash of a block.
        :type block_hash: str
        :param tx_objects: (optionnal) If true it returns the full transaction objects, if false only the hashes of the transactions.
        :type tx_objects: Boolean
        :return: A block object, or null when no block was found
        :rtype: dict

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getBlockByHash('0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b')
        {'difficulty': '0xaa41aea7beb9e',
         'extraData': '0x6e616e6f706f6f6c2e6f7267',
         'gasLimit': '0x7a121d',
         'gasUsed': '0x614398',
         'hash': '0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b',
         'logsBloom': '0x000001052440040410040000008006000020000002a11000308045410029410802804801080040c00880000002010c0201804010100900b0000001000240000010800040080044910000010c0000204a041140220008000040000040808800404020802226400018144000400484880012000408000401400000211000c000e2040000209000040080c00000c000890080001090008000001000000102000100002400082240104010400000420080041004050a1080c0042000000000080ac000000802020400001009088021040230000000249208020621000022001820180500200000820002600004888840810420200080100400080000ac0004100000',
         'miner': '0x52bc44d5378309ee2abf1539bf71de1b7d7be3b5',
         'mixHash': '0xa79e0692e7056ea2af26a78a1ed42ac7f3049eb322041c073e5d5a08f6c7e053',
         'nonce': '0x6677371ca8459875',
         'number': '0x4dd2a4',
         [...]
         'totalDifficulty': '0x8b344e12294352eee8',
         'transactions': [{
            [...]
         'value': '0x0'}],
        'transactionsRoot': '0x184cd24c9f45c66ff3846c48fb63e24094aa5909cabfd38211c1d8209128cbc0',
        'uncles': []}

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbyhash
        .. todo::
            TESTED
        """
        return self.call('eth_getBlockByHash', [block_hash, tx_objects])

    def eth_getBlockByNumber(self, block=BLOCK_TAG_LATEST, tx_objects=True):
        """ Returns information about a block by hash.

        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :param tx_objects: (optionnal) If true it returns the full transaction objects, if false only the hashes of the transactions.
        :type tx_objects: Boolean
        :return: A block object, or null when no block was found
        :rtype: dict

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getBlockByNumber(5100196)
        {'difficulty': '0xaa41aea7beb9e',
         'extraData': '0x6e616e6f706f6f6c2e6f7267',
         'gasLimit': '0x7a121d',
         'gasUsed': '0x614398',
         'hash': '0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b',
         'logsBloom': '0x000001052440040410040000008006000020000002a11000308045410029410802804801080040c00880000002010c0201804010100900b0000001000240000010800040080044910000010c0000204a041140220008000040000040808800404020802226400018144000400484880012000408000401400000211000c000e2040000209000040080c00000c000890080001090008000001000000102000100002400082240104010400000420080041004050a1080c0042000000000080ac000000802020400001009088021040230000000249208020621000022001820180500200000820002600004888840810420200080100400080000ac0004100000',
         'miner': '0x52bc44d5378309ee2abf1539bf71de1b7d7be3b5',
         'mixHash': '0xa79e0692e7056ea2af26a78a1ed42ac7f3049eb322041c073e5d5a08f6c7e053',
         'nonce': '0x6677371ca8459875',
         'number': '0x4dd2a4',
         [...]
         'totalDifficulty': '0x8b344e12294352eee8',
         'transactions': [{
            [...]
         'value': '0x0'}],
        'transactionsRoot': '0x184cd24c9f45c66ff3846c48fb63e24094aa5909cabfd38211c1d8209128cbc0',
        'uncles': []}

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getblockbynumber
        .. todo::
            TESTED
        """
        block = validate_block(block)
        return self.call('eth_getBlockByNumber', [block, tx_objects])

    def eth_getTransactionByHash(self, tx_hash):
        """ Returns the information about a transaction requested by transaction hash.

        :param tx_hash:  32 Bytes - hash of a transaction
        :type tx_hash: str
        :return: A transaction object, or null when no transaction was found
        :rtype: dict

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getTransactionByHash('0x345303843c2f3041d12f0c5e6075fd294c2e2ca8cd9b4a9addca3f8caf4380ff')
        {'blockHash': '0xaedd5193cb2b2d9de4c371404277468c7e30eb96f8f9990bd964ca535d88ebc4',
         'blockNumber': '0x4dd3b0',
         'from': '0xc5ff88c3e2902c56c0278fa0e7062d4b5c7e9358',
         'gas': '0x5208',
         'gasPrice': '0xbebc200',
         'hash': '0x345303843c2f3041d12f0c5e6075fd294c2e2ca8cd9b4a9addca3f8caf4380ff',
         'input': '0x',
         'nonce': '0x1',
         'r': '0x5b43f56b69bc78571de39b1b1fc33905a4af588a2ce59f31c54bc54391a255b8',
         's': '0x359e7889447314fb8d9a7e526852471c7bccee006f47222499f9353074107910',
         'to': '0xf954bbabe7bf9a2a4c98dceb293bf437e3863a4e',
         'transactionIndex': '0x66',
         'v': '0x25',
         'value': '0x3202c66793000'}

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyhash
        .. todo::
            TESTED
        """
        return self.call('eth_getTransactionByHash', [tx_hash])

    def eth_getTransactionByBlockHashAndIndex(self, block_hash, index=0):
        """ Returns information about a transaction by block hash and transaction index position.

        :param tx_hash:  32 Bytes - hash of a transaction
        :type tx_hash: str
        :param index: (optionnal) integer of the transaction index position.
        :type index: int
        :return: A transaction object, or null when no transaction was found
        :rtype: dict

        .. seealso::
            :method:`eth_getTransactionByHash`
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblockhashandindex
        .. todo::
            NOT TESTED
        """
        return self.call('eth_getTransactionByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getTransactionByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        """ Returns information about a transaction by block number and transaction index position.

        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :param index: (optionnal) integer of the transaction index position.
        :type index: int
        :return: A transaction object, or null when no transaction was found
        :rtype: dict

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getTransactionByBlockNumberAndIndex(5100196, 1)
        {'blockHash': '0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b',
         'blockNumber': '0x4dd2a4',
         'from': '0xb01cb49fe0d6d6e47edf3a072d15dfe73155331c',
         'gas': '0x5208',
         'gasPrice': '0xe33e22200',
         'hash': '0xf02ffa405bae96e62a9e36fbd781362ca378ec62353d5e2bd0585868d3deaf61',
         'input': '0x',
         'nonce': '0x1908f',
         'r': '0xcad900a5060ba9bb646a7f6965f98e945d71a19b3e30ff53d03b9797c6153d07',
         's': '0x53b11a48758fc383df878a9b5468c83b033f5036b124b16dbb0a5167aee7fc4f',
         'to': '0x26cd018553871f2e887986bc24c68a0ce622bb8f',
         'transactionIndex': '0x1',
         'v': '0x25',
         'value': '0x1bc16d674ec80000'}

        .. seealso::
            :method:`eth_getTransactionByHash`
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionbyblocknumberandindex
        .. todo::
            TESTED
        """
        block = validate_block(block)
        return self.call('eth_getTransactionByBlockNumberAndIndex', [block, hex(index)])

    def eth_getTransactionReceipt(self, tx_hash):
        """ Returns the receipt of a transaction by transaction hash.

        :param tx_hash: 32 Bytes - hash of a transaction
        :type tx_hash: str
        :return: A transaction receipt object, or null when no receipt was found
        :rtype: dict

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_getTransactionReceipt('0xf02ffa405bae96e62a9e36fbd781362ca378ec62353d5e2bd0585868d3deaf61')
        {'blockHash': '0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b',
         'blockNumber': '0x4dd2a4',
         'contractAddress': None,
         'cumulativeGasUsed': '0xe2d7',
         'from': '0xb01cb49fe0d6d6e47edf3a072d15dfe73155331c',
         'gasUsed': '0x5208',
         'logs': [],
         'logsBloom': '0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000',
         'status': '0x1',
         'to': '0x26cd018553871f2e887986bc24c68a0ce622bb8f',
         'transactionHash': '0xf02ffa405bae96e62a9e36fbd781362ca378ec62353d5e2bd0585868d3deaf61',
         'transactionIndex': '0x1'}

        .. note::
            That the receipt is not available for pending transactions.
        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_gettransactionreceipt
        .. todo::
            TESTED

        """
        return self.call('eth_getTransactionReceipt', [tx_hash])

    def eth_getUncleByBlockHashAndIndex(self, block_hash, index=0):
        """ Returns information about a uncle of a block by hash and uncle index position.

        :param tx_hash:  32 Bytes - hash of a transaction
        :type tx_hash: str
        :param index: (optionnal)  the uncle's index position.
        :type index: int
        :return: A block object, or null when no block was found
        :rtype: dict

        .. note::
            An uncle doesn't contain individual transactions.
        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblockhashandindex
        .. todo::
            NOT TESTED
        """
        return self.call('eth_getUncleByBlockHashAndIndex', [block_hash, hex(index)])

    def eth_getUncleByBlockNumberAndIndex(self, block=BLOCK_TAG_LATEST, index=0):
        """ Returns information about a uncle of a block by number and uncle index position.

        :param block: (optionnal) integer block number, or the string "latest", "earliest" or "pending"
        :type block: int or str
        :param index: (optionnal) the uncle's index position.
        :type index: int
        :return: A block object, or null when no block was found
        :rtype: dict

        .. note::
            An uncle doesn't contain individual transactions.
        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getunclebyblocknumberandindex
        .. todo::
            NOT TESTED
        """
        block = validate_block(block)
        return self.call('eth_getUncleByBlockNumberAndIndex', [block, hex(index)])

    def eth_getCompilers(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getcompilers

        NOT WORKING
        """
        return self.call('eth_getCompilers')

    def eth_compileSolidity(self, code):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilesolidity

        NOT WORKING
        """
        return self.call('eth_compileSolidity', [code])

    def eth_compileLLL(self, code):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compilelll

        N/A
        """
        return self.call('eth_compileLLL', [code])

    def eth_compileSerpent(self, code):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_compileserpent

        N/A
        """
        return self.call('eth_compileSerpent', [code])

    def eth_newFilter(self, from_block=BLOCK_TAG_LATEST, to_block=BLOCK_TAG_LATEST, address=None, topics=None):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newfilter

        NEEDS TESTING
        """
        _filter = {
            'fromBlock': from_block,
            'toBlock': to_block,
            'address': address,
            'topics': topics,
        }
        return self.call('eth_newFilter', [_filter])

    def eth_newBlockFilter(self):
        """ Creates a filter in the node, to notify when a new block arrives. To check if the state has changed, call eth_getFilterChanges.

        :return: A filter id.
        :rtype: hex str

        :Example:

        >>> explorer = EthereumExplorerRPC()
        >>> explorer.eth_newBlockFilter()
        '0x1d21d3c44b9a1501d4358a44bdb6da1d'

        .. seealso::
            https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newblockfilter
        .. todo::
            TESTED
        """
        return self.call('eth_newBlockFilter')

    def eth_newPendingTransactionFilter(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_newpendingtransactionfilter

        TESTED
        """
        return hex_to_dec(self.call('eth_newPendingTransactionFilter'))

    def eth_uninstallFilter(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_uninstallfilter

        NEEDS TESTING
        """
        return self.call('eth_uninstallFilter', [filter_id])

    def eth_getFilterChanges(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterchanges

        NEEDS TESTING
        """
        return self.call('eth_getFilterChanges', [filter_id])

    def eth_getFilterLogs(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getfilterlogs

        NEEDS TESTING
        """
        return self.call('eth_getFilterLogs', [filter_id])

    def eth_getLogs(self, filter_object):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getlogs

        NEEDS TESTING
        """
        return self.call('eth_getLogs', [filter_object])

    def eth_getWork(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_getwork

        TESTED
        """
        return self.call('eth_getWork')

    def eth_submitWork(self, nonce, header, mix_digest):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submitwork

        NEEDS TESTING
        """
        return self.call('eth_submitWork', [nonce, header, mix_digest])

    def eth_submitHashrate(self, hash_rate, client_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#eth_submithashrate

        TESTED
        """
        return self.call('eth_submitHashrate', [hex(hash_rate), client_id])

    def db_putString(self, db_name, key, value):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_putstring

        TESTED
        """
        warnings.warn('deprecated', DeprecationWarning)
        return self.call('db_putString', [db_name, key, value])

    def db_getString(self, db_name, key):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_getstring

        TESTED
        """
        warnings.warn('deprecated', DeprecationWarning)
        return self.call('db_getString', [db_name, key])

    def db_putHex(self, db_name, key, value):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_puthex

        TESTED
        """
        if not value.startswith('0x'):
            value = '0x{}'.format(value)
        warnings.warn('deprecated', DeprecationWarning)
        return self.call('db_putHex', [db_name, key, value])

    def db_getHex(self, db_name, key):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#db_gethex

        TESTED
        """
        warnings.warn('deprecated', DeprecationWarning)
        return self.call('db_getHex', [db_name, key])

    def shh_version(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_version

        N/A
        """
        return self.call('shh_version')

    def shh_post(self, topics, payload, priority, ttl, from_=None, to=None):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_post

        NEEDS TESTING
        """
        whisper_object = {
            'from': from_,
            'to': to,
            'topics': topics,
            'payload': payload,
            'priority': hex(priority),
            'ttl': hex(ttl),
        }
        return self.call('shh_post', [whisper_object])

    def shh_newIdentity(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newidentity

        N/A
        """
        return self.call('shh_newIdentity')

    def shh_hasIdentity(self, address):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_hasidentity

        NEEDS TESTING
        """
        return self.call('shh_hasIdentity', [address])

    def shh_newGroup(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newgroup

        N/A
        """
        return self.call('shh_newGroup')

    def shh_addToGroup(self):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_addtogroup

        NEEDS TESTING
        """
        return self.call('shh_addToGroup')

    def shh_newFilter(self, to, topics):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_newfilter

        NEEDS TESTING
        """
        _filter = {
            'to': to,
            'topics': topics,
        }
        return self.call('shh_newFilter', [_filter])

    def shh_uninstallFilter(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_uninstallfilter

        NEEDS TESTING
        """
        return self.call('shh_uninstallFilter', [filter_id])

    def shh_getFilterChanges(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getfilterchanges

        NEEDS TESTING
        """
        return self.call('shh_getFilterChanges', [filter_id])

    def shh_getMessages(self, filter_id):
        """
        https://github.com/ethereum/wiki/wiki/JSON-RPC#shh_getmessages

        NEEDS TESTING
        """
        return self.call('shh_getMessages', [filter_id])


class EthereumInfuraExplorer(EthereumExplorerRPC):
    """
    EthereumExplorer subclass for using Infura
    """

    def __init__(self, key=INFURA_APIKEY, network=INFURA_MAINNET):
        EthereumExplorerRPC.__init__(self, host=network + key,
                                     port=INFURA_RPC_PORT, tls=True)


class EthereumParityExplorer(EthereumExplorerRPC):
    """
    EthereumExplorer subclass for Parity-specific methods
    """

    def __init__(self, host='localhost', port=PARITY_DEFAULT_RPC_PORT, tls=False):
        EthereumExplorerRPC.__init__(self, host=host, port=port, tls=tls)

    def trace_filter(self, from_block=None, to_block=None, from_addresses=None, to_addresses=None):
        """
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_filter

        TESTED
        """
        params = {}
        if from_block is not None:
            from_block = validate_block(from_block)
            params['fromBlock'] = from_block
        if to_block is not None:
            to_block = validate_block(to_block)
            params['toBlock'] = to_block
        if from_addresses is not None:
            if not isinstance(from_addresses, list):
                from_addresses = [from_addresses]
            params['fromAddress'] = from_addresses
        if to_addresses is not None:
            if not isinstance(to_addresses, list):
                to_addresses = [to_addresses]
            params['toAddress'] = to_addresses
        return self.call('trace_filter', [params])

    def trace_get(self, tx_hash, positions):
        """
        https://wiki.parity.io/JSONRPC
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_get

        NEEDS TESTING
        """
        if not isinstance(positions, list):
            positions = [positions]
        return self.call('trace_get', [tx_hash, positions])

    def trace_transaction(self, tx_hash):
        """
        https://wiki.parity.io/JSONRPC
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_transaction

        NEEDS TESTING
        """
        return self.call('trace_transaction', [tx_hash])

    def trace_block(self, block=BLOCK_TAG_LATEST):
        """
        https://wiki.parity.io/JSONRPC
        https://github.com/ethcore/parity/wiki/JSONRPC-trace-module#trace_block

        NEEDS TESTING
        """
        block = validate_block(block)
        return self.call('trace_block', [block])
