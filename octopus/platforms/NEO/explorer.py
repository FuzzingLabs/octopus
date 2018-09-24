from octopus.engine.explorer import Explorer

# Inspired by https://github.com/ellmetha/neojsonrpc

NEO_HOST = 'seed2.neo.org'

MAINNET_HTTP_RPC_PORT = 10332
MAINNET_HTTPS_RPC_PORT = 10331
TESTNET_HTTP_RPC_PORT = 20332
TESTNET_HTTPS_RPC_PORT = 20331


class NeoExplorerRPC(Explorer):
    '''
    Neo JSON-RPC client class
    '''

    def __init__(self, host=NEO_HOST, port=MAINNET_HTTP_RPC_PORT, tls=False, max_retries=3):
        Explorer.__init__(self, host=host, port=port, tls=tls, max_retries=max_retries)

        # Initializes an "ID counter" that'll be used to forge each request to the JSON-RPC
        # endpoint. The "id" parameter is "required" in order to help clients sort responses out.
        # In the case of the current client, we'll just ensure that this value gets incremented
        # after each request made to the JSON-RPC endpoint.
        self._id_counter = 0

    def call(self, method, params=None, jsonrpc='2.0', _id=None):

        # Determines which 'id' value to use and increment the counter associated with the current
        # client instance if applicable.
        rid = _id or self._id_counter
        if _id is None:
            self._id_counter += 1

        return super().call(method, params, jsonrpc, rid)

    #######################
    # HIGHT-LEVEL METHODS #
    #######################

    def get_transaction(self, transaction_id, verbosity=True):
        """ Return transaction informations

        .. seealso::
            :method:`getrawtransaction`
        """
        return self.getrawtransaction(transaction_id, verbosity)

    def get_block_by_number(self, block_number):
        """ Return block information using given block number

        .. seealso::
            :method:`getblock`
        """
        return self.getblock(block_number)

    def get_block_by_hash(self, block_hash):
        """ Return block information using given block hash

        .. seealso::
            :method:`getblock`
        """
        return self.getblock(block_hash)

    ####################
    # JSON-RPC METHODS #
    ####################

    # ressources :
    # http://docs.neo.org/en-us/node/api.html
    # https://neotracker.io/

    def dumpprivkey(self, address):
        """ Returns the private key of the standard address.

        :param address: a 34-bit length address (eg. AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz)
        :type address: str
        :return: Returns the private key of the standard address.
        :rtype: str

        .. note::
            You need to open the wallet in the NEO-CLI node before you execute this command.
        .. seealso::
            http://docs.neo.org/en-us/node/api/dumpprivkey.html
        .. todo::
            SEEM TO WORK
        """
        return self.call('dumpprivkey', [address])

    def getaccountstate(self, address):
        """ Returns the account state information associated with a specific address.

        :param address: a 34-bit length address (eg. AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz)
        :type address: str
        :return: dictionary containing the account state information
        :rtype: dict

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getaccountstate("AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz")
        {'balances': [{'asset': '0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b',
            'value': '60'},
        {'asset': '0x602c79718b16e442de58778e148d0b1084e3b2dffd5de6b7b16cee7969282de7',
            'value': '0.29359449'}],
        'frozen': False,
        'script_hash': '0xb6be270ca7cf0affe93de076fc3ace8662027f61',
        'version': 0,
        'votes': []}

        .. seealso::
            http://docs.neo.org/en-us/node/api/getaccountstate.html
        .. todo::
            TESTED

        """
        return self.call('getaccountstate', [address])

    def getapplicationlog(self, txid):
        """ Returns the contract log based on the specified txid.

        :param txid: Transaction ID
        :type txid: str
        :return: dictionary containing the contract logs
        :rtype: dict

        .. note::
            You need to run the command dotnet neo-cli.dll --log to enable logging before invoking this method. The complete contract logs are stored under the ApplicationLogs directory.
        .. seealso::
            http://docs.neo.org/en-us/node/api/getapplicationlog.html
        .. todo::
            NOT TESTED
        """
        return self.call('getapplicationlog', [txid])

    def getassetstate(self, asset_id):
        """ Returns the asset information associated with a specific asset ID.

        :param asset_id:
            an asset identifier (the transaction ID of the RegistTransaction when the asset is
            registered)
        :type asset_id: str
        :return: dictionary containing the asset state information
        :rtype: dict

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getassetstate("c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b")
        {'admin': 'Abf2qMs1pzQb8kYk9RuxtUb9jtRKJVuBJt',
         'amount': '100000000',
         'available': '100000000',
         'expiration': 4000000,
         'frozen': False,
         'id': '0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b',
         'issuer': 'Abf2qMs1pzQb8kYk9RuxtUb9jtRKJVuBJt',
         'name': [{'lang': 'zh-CN', 'name': '小蚁股'},
         {'lang': 'en', 'name': 'AntShare'}],
         'owner': '00',
         'precision': 0,
         'type': 'GoverningToken',
         'version': 0}

        .. seealso::
            http://docs.neo.org/en-us/node/api/getassetstate.html
        .. todo::
            TESTED
        """
        return self.call('getassetstate', [asset_id])

    def getbalance(self, asset_id):
        """ Returns the balance of the corresponding asset in the wallet, based on the specified asset number.

        :param asset_id:
            an asset identifier (the transaction ID of the RegistTransaction when the asset is
            registered)
        :type asset_id: str
        :return: dictionary containing the actual balance and the exact amount of the asset in the wallet
        :rtype: dict

        .. note::
            You need to open the wallet in the NEO-CLI node before you execute this command.
        .. seealso::
            http://docs.neo.org/en-us/node/api/getbalance.html
        .. todo::
            NOT TESTED
        """
        return self.call('getbalance', [asset_id])

    def getbestblockhash(self):
        """ Returns the hash of the tallest block in the main chain.
        :return: hash of the tallest block in the chain
        :rtype: str

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getbestblockhash()
        '0x881da7e14680cd4a020aa503dc602a92a411ad3184b6b14789074c775fbe5b7b'

        .. seealso::
            http://docs.neo.org/en-us/node/api/getbestblockhash.html
        .. todo::
            TESTED
        """
        return self.call('getbestblockhash')

    def getblock(self, block_id, verbose=True):
        """ Returns the block information associated with a specific hash value or block index.

        :param block_hash: a block hash value or a block index (block height)
        :param verbose:
            a boolean indicating whether the detailed block information should be returned in JSON
            format (otherwise the block information is returned as an hexadecimal string by the
            JSON-RPC endpoint)
        :type block_hash: str or int
        :type verbose: bool
        :return:
            dictionary containing the block information (or an hexadecimal string if verbose is set
            to False)
        :rtype: dict or str

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getblock(1917115)
        {'confirmations': 1,
         'hash': '0x881da7e14680cd4a020aa503dc602a92a411ad3184b6b14789074c775fbe5b7b',
         'index': 1917115,
         .....
        >>> explorer.getblock('0x881da7e14680cd4a020aa503dc602a92a411ad3184b6b14789074c775fbe5b7b')
        {'confirmations': 1,
         'hash': '0x881da7e14680cd4a020aa503dc602a92a411ad3184b6b14789074c775fbe5b7b',
         'index': 1917115,

        .. seealso::
            http://docs.neo.org/en-us/node/api/getblock.html
            http://docs.neo.org/en-us/node/api/getblock2.html
        .. todo::
            TESTED
        """
        return self.call('getblock', [block_id, int(verbose)])

    def getblockcount(self):
        """ Returns the number of blocks in the chain.
        :return: number of blocks in the chain
        :rtype: int

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getblockcount()
        1917116

        .. seealso::
            http://docs.neo.org/en-us/node/api/getblockcount.html
        .. todo::
            TESTED
        """
        return self.call('getblockcount')

    def getblockhash(self, block_index):
        """ Returns the hash value associated with a specific block index.
        :param block_index: a block index (block height)
        :type block_index: int
        :return: hash of the block associated with the considered index
        :rtype: str

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getblockhash(1917115)
        '0x881da7e14680cd4a020aa503dc602a92a411ad3184b6b14789074c775fbe5b7b'

        .. seealso::
            http://docs.neo.org/en-us/node/api/getblockhash.html
        .. todo::
            TESTED
        """
        return self.call('getblockhash', [block_index])

    def getblocksysfee(self, block_index):
        """ Returns the system fees associated with a specific block index.
        :param block_index: a block index (block height)
        :type block_index: int
        :return: system fees of the block, expressed in NeoGas units
        :rtype: str

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getblocksysfee(1917115)
        '206594'

        .. seealso::
            http://docs.neo.org/en-us/node/api/getblocksysfee.html
        .. todo::
            TESTED
        """
        return self.call('getblocksysfee', [block_index])

    def getconnectioncount(self):
        """ Returns the current number of connections for the considered node.
        :return: number of connections for the node
        :rtype: int

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getconnectioncount()
        57

        .. seealso::
            http://docs.neo.org/en-us/node/api/getconnectioncount.html
        .. todo::
            TESTED
        """
        return self.call('getconnectioncount')

    def getcontractstate(self, script_hash):
        """ Returns the contract information associated with a specific script hash.
        :param script_hash: contract script hash
        :type script_hash: str
        :return: dictionary containing the contract information
        :rtype: dict

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getcontractstate("d3cce84d0800172d09c88ccad61130611bd047a4")
        {'author': 'Erik Zhang',
         'code_version': '2.0',
         'description': 'Lock 2.0',
         'email': 'erik@neo.org',
         'hash': '0xd3cce84d0800172d09c88ccad61130611bd047a4',
         'name': 'Lock',
         'parameters': ['Integer', 'PublicKey', 'Signature'],
         'returntype': 'Boolean',
         'script': '56c56b6c766b00527ac46c766b51527ac46c766b52527ac4616168184e656f2e426c6f636b636861696e2e4765744865696768746168184e656f2e426c6f636b636861696e2e4765744865616465726c766b53527ac46c766b00c36c766b53c36168174e656f2e4865616465722e47657454696d657374616d70a06c766b54527ac46c766b54c3640e00006c766b55527ac4621a006c766b51c36c766b52c3617cac6c766b55527ac46203006c766b55c3616c7566',
         'storage': False,
         'version': 0}

        .. seealso::
            http://docs.neo.org/en-us/node/api/getcontractstate.html
        .. todo::
            TESTED
        """
        return self.call('getcontractstate', [script_hash])

    def getnewaddress(self):
        """ Creates a new address and return it.
        :return: the newly created address.
        :rtype: str

        .. note::
            You need to open the wallet in the NEO-CLI node before you execute this command.
        .. seealso::
            http://docs.neo.org/en-us/node/api/getnewaddress.html
        .. todo::
            NOT TESTED
        """
        return self.call('getnewaddress')

    def getrawmempool(self):
        """ Returns a list of unconfirmed transactions in memory associated with the node.
        :return: list of unconfirmed transaction hashes
        :rtype: list

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.getrawmempool()
        ['0xb7ed3825dfb23db0198df1d00b7250a867b1b7457b0f5ec9c0f9393ad1939729',
         '0x4393c79340eb9e11fe6a179984b6989195044c79b92dee16a8a1090189b8ef4d',
         '0xa705e48ab47817409028d89bf5727399333cdefe60d879ac5b70df38f3096436',
         ...

        .. seealso::
            http://docs.neo.org/en-us/node/api/getrawmempool.html
        .. todo::
            TESTED
        """
        return self.call('getrawmempool')

    def getrawtransaction(self, tx_hash, verbose=True):
        """ Returns detailed information associated with a specific transaction hash.

        :param tx_hash: transaction hash
        :param verbose:
            a boolean indicating whether the detailed transaction information should be returned in
            JSON format (otherwise the transaction information is returned as an hexadecimal string
            by the JSON-RPC endpoint)
        :type tx_hash: str
        :type verbose: bool
        :return:
            dictionary containing the transaction information (or an hexadecimal string if verbose
            is set to False)
        :rtype: dict or str

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> tx_id = "f4250dab094c38d8265acc15c366dc508d2e14bf5699e12d9df26577ed74d657"
        >>> explorer.getrawtransaction(tx_id, False)
        '80000001195876cb34364dc38b730077156c6bc3a7fc570044a66fbfeeea56f71327e8ab000[...]dac'
        >>> explorer.getrawtransaction(tx_id)
        {'attributes': [],
         'blockhash': '0x9c814276156d33f5dbd4e1bd4e279bb4da4ca73ea7b7f9f0833231854648a72c',
         'blocktime': 1496719422,
         'confirmations': 925250,
         'net_fee': '0',
         'scripts': [{'invocation': '40915467ecd359684b2dc358024ca750609591aa731a0b309c7fb3cab5cd0836ad3992aa0a24da431f43b68883ea5651d548feb6bd3c8e16376e6e426f91f84c58',
           'verification': '2103322f35c7819267e721335948d385fae5be66e7ba8c748ac15467dcca0693692dac'}],
         'size': 262,
         'sys_fee': '0',
         'txid': '0xf4250dab094c38d8265acc15c366dc508d2e14bf5699e12d9df26577ed74d657',
         'type': 'ContractTransaction',
         'version': 0,
         'vin': [{'txid': '0xabe82713f756eaeebf6fa6440057fca7c36b6c157700738bc34d3634cb765819',
           'vout': 0}],
         'vout': [{'address': 'AHCNSDkh2Xs66SzmyKGdoDKY752uyeXDrt',
           'asset': '0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b',
           'n': 0,
           'value': '2950'},
          {'address': 'ALDCagdWUVV4wYoEzCcJ4dtHqtWhsNEEaR',
           'asset': '0xc56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b',
           'n': 1,
           'value': '4050'}]}

        .. seealso::
            http://docs.neo.org/en-us/node/api/getrawtransaction.html
        .. todo::
            TESTED
        """
        return self.call('getrawtransaction', [tx_hash, int(verbose)])

    def getstorage(self, script_hash, hexkey):
        """ Returns the value stored in the storage of a contract script hash for a given key.

        :param script_hash: contract script hash
        :param hexkey: key to look up in the storage (in hex string)
        :type script_hash: str
        :type key: str
        :return: the stored value (in hex string)
        :rtype: str

        .. seealso::
            http://docs.neo.org/en-us/node/api/getstorage.html
        .. todo::
            SEEM TO WORK
        """
        return self.call('getstorage', [script_hash, hexkey])

    def gettxout(self, tx_hash, index):
        """ Returns the transaction output information corresponding to a hash and index.

        :param tx_hash: transaction hash
        :param index:
            index of the transaction output to be obtained in the transaction (starts from 0)
        :type tx_hash: str
        :type index: int
        :return: dictionary containing the transaction output
            If the transaction output is already spent, the result value will be null.
        :rtype: dict

        .. seealso::
            http://docs.neo.org/en-us/node/api/gettxout.html
        .. todo::
            SEEM TO WORK
        """
        return self.call('gettxout', [tx_hash, index])

    def getpeers(self):
        """ Returns a list of nodes that the node is currently connected/disconnected from.
        :return: dictionary containing the nodes the current node is connected/disconnected from
        :rtype: dict

        .. seealso::
            http://docs.neo.org/en-us/node/api/getpeers.html
        .. todo::
            NOT TESTED
        """
        return self.call('getpeers', [])

    def getversion(self):
        """ Returns version information about the current node.
        :return: dictionary containing version information about the current node
        :rtype: dict

        .. seealso::
            http://docs.neo.org/en-us/node/api/getversion.html
        .. todo::
            NOT TESTED
        """
        return self.call('getversion')

    def invoke(self, script_hash, params):
        """ Invokes a contract with given parameters and returns the result.
        It should be noted that the name of the function invoked in the contract should be part of
        paramaters.

        :param script_hash: contract script hash
        :param params: list of parameters to be passed in to the smart contract
        :type script_hash: str
        :type params: list
        :return: result of the invocation
        :rtype: dictionary

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.invoke("dc675afc61a7c0f7b3d2682bf6e1d8ed865a0e5f",
            [{"type": "String","value": "name"},{"type":"Boolean","value": False}])
        {'gas_consumed': '0.01',
         'stack': [{'type': 'ByteArray', 'value': ''},
          {'type': 'ByteArray', 'value': '6e616d65'}],
         'state': 'FAULT, BREAK'}

        .. note::
            This method is to test your VM script as if they were ran on the blockchain at that point in time. This RPC call does not affect the blockchain in any way.
        .. seealso::
            http://docs.neo.org/en-us/node/api/invoke.html
        .. todo::
            SEEM TO WORK
        """
        return self.call('invoke', [script_hash, params])

    def invokefunction(self, script_hash, operation, params):
        """ Invokes a contract's function with given parameters and returns the result.

        :param script_hash: contract script hash
        :param operation: name of the operation to invoke
        :param params: list of paramaters to be passed in to the smart contract
        :type script_hash: str
        :type operation: str
        :type params: list
        :return: result of the invocation
        :rtype: dictionary

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> script_hash = "ecc6b20d3ccac1ee9ef109af5a7cdb85706b1df9"
        >>> explorer.invokefunction(script_hash, "balanceOf", [{"type": "Hash160", "value": "bfc469dd56932409677278f6b7422f3e1f34481d"}])
        {'gas_consumed': '0.338',
         'stack': [{'type': 'ByteArray', 'value': '00ab510d'}],
         'state': 'HALT, BREAK'}

        .. note::
            This method is to test your VM script as if they were ran on the blockchain at that point in time. This RPC call does not affect the blockchain in any way.
        .. seealso::
            http://docs.neo.org/en-us/node/api/invokefunction.html
        .. todo::
            TESTED
        """
        return self.call('invokefunction', [script_hash, operation, params])

    def invokescript(self, script):
        """ Invokes a script on the VM and returns the result.
        :param script: script runnable by the VM
        :type script: str
        :return: result of the invocation
        :rtype: dictionary

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.invokescript("00046e616d656711c4d1f4fba619f2628870d36e3a9773e874705b")
        {'gas_consumed': '0.01',
         'stack': [{'type': 'ByteArray', 'value': ''},
          {'type': 'ByteArray', 'value': '6e616d65'}],
         'state': 'FAULT, BREAK'}

        .. note::
            This method is to test your VM script as if they were ran on the blockchain at that point in time. This RPC call does not affect the blockchain in any way.
        .. seealso::
            http://docs.neo.org/en-us/node/api/invokescript.html
        .. todo::
            TESTED
        """
        return self.call('invokescript', [script])

    def listaddress(self):
        """ Lists all the addresses in the current wallet.
        :return: dictionary containing addresses in the wallet and indicates whether it is a watch only address.
        :rtype: dict

        .. note::
            You need to open the wallet in the NEO-CLI node before invoking this method.
        .. seealso::
            http://docs.neo.org/en-us/node/api/listaddress.html
        .. todo::
            NOT TESTED
        """
        return self.call('listaddress')

    def sendrawtransaction(self, hextx):
        """ Broadcasts a transaction over the NEO network and returns the result.
        :param hextx: hexadecimal string that has been serialized
        :type hextx: str
        :return: result of the transaction
        :rtype: bool

        .. seealso::
            http://docs.neo.org/en-us/node/api/sendrawtransaction.html
        .. todo::
            NOT TESTED
        """
        return self.call('sendrawtransaction', [hextx])

    def sendtoaddress(self, asset_id, address, value, fee=0):
        """ Transfers to the specified address.

        :param asset_id:
            an asset identifier (the transaction ID of the RegistTransaction when the asset is
            registered)
        :type asset_id: str
        :param address: a 34-bit length address (eg. AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz)
        :type address: str
        :param value: amount to transfer
        :type value: int
        :param fee: Fee, default value is 0 (optional parameter)
        :type fee: int
        :return:
            dictionary containing the asset state information
            If the signature is incomplete, it will return the transaction to be signed.
            If the balance is insufficient, it will return an error message.
        :rtype: dict or str

        .. note::
            You need to open the wallet in the Neo-CLI node before you execute this command.
        .. seealso::
            http://docs.neo.org/en-us/node/api/sendtoaddress.html
        .. todo::
            NOT TESTED
        """
        return self.call('sendtoaddress', [asset_id, address, value, fee])

    def sendmany(self, outputs_array, fee=0, change_address=None):
        """ Bulk transfer order, and you can specify a change address.

        :param outputs_array: Array, the data structure of each element in the array is as follows:
            {"asset": <asset>,"value": <value>,"address": <address>}
            :param asset:
                an asset identifier (the transaction ID of the RegistTransaction when the asset is
                registered)
            :type asset: str
            :param value: Transfer amount
            :type value: int
            :param address: a 34-bit length destination address (eg. AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz)
            :type address: str
        :type outputs_array: list
        :param fee: Handling fee, optional parameter, default is 0.
        :type fee: int
        :param change_address: Change address, optional parameter, default is the first standard address in the wallet.
        :type change_address: str
        :return:
            Returns the transaction details as above to indicate that the transaction was sent successfully or the transaction failed.
            If the JSON format is incorrect, a Parse error is returned.
            If the signature is incomplete, a pending transaction is returned.
            If the balance is insufficient, an error message is returned.
        :rtype: dict or str

        .. note::
            You need to open the wallet in the Neo-CLI node before you execute this command.
        .. seealso::
            http://docs.neo.org/en-us/node/api/sendmany.html
        .. todo::
            NOT TESTED
        """
        return self.call('sendmany')

    def submitblock(self, hex_string):
        """ Submit new blocks

        No documentation about this RPC methods (but described as API)

        .. note::
            Needs to be a consensus node
        .. seealso::
            https://github.com/neo-project/docs/blob/master/en-us/node/api.md
        .. todo::
            NOT TESTED
        """
        return self.call('submitblock', [hex_string])

    def validateaddress(self, address):
        """ Validates if the considered string is a valid NEO address.

        :param address: string containing a potential NEO address
        :type address: str
        :return: dictionary containing the result of the verification
        :rtype: dictionary

        :Example:

        >>> explorer = NeoExplorerRPC()
        >>> explorer.validateaddress("AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz")
        {'address': 'AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz', 'isvalid': True}

        .. seealso::
            http://docs.neo.org/en-us/node/api/validateaddress.html

        """
        return self.call('validateaddress', [address])
