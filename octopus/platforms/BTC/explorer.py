from octopus.engine.explorer import Explorer
from octopus.platforms.BTC.bech32 import encode as bech32_encode

import binascii

RPC_USER = 'test'
RPC_PASSWORD = 'test'
RPC_HOST = 'localhost'

BITCOIND_DEFAULT_RPC_PORT = 8332

class BitcoinExplorerRPC(Explorer):
    '''
    Bitcoin JSON-RPC client class
    '''

    def __init__(self, host='localhost', port=BITCOIND_DEFAULT_RPC_PORT, tls=False, max_retries=3):
        Explorer.__init__(self, host=host, port=port, tls=tls, max_retries=max_retries)

    def call(self, method, params=None, jsonrpc='2.0', _id=None):
        return super().call(method, params, jsonrpc, _id)

    #######################
    # HIGHT-LEVEL METHODS #
    #######################

    def get_transaction(self, transaction_id, verbosity=1):
        """ Return transaction informations

        .. seealso::
            getrawtransaction()
        """
        return self.getrawtransaction(transaction_id, verbosity)

    def get_block_by_number(self, block_number):
        """ Return block information using given block number

        .. seealso::
            getblockhash() + getblock()
        """
        return self.getblock(self.getblockhash(block_number))

    def get_block_by_hash(self, block_hash):
        """ Return block information using given block hash

        .. seealso::
            getblock()
        """
        return self.getblock(block_hash)

    def decode_tx(self, tx):

        result = {"txid": tx['txid'],
                  "sender": [],
                  "receiver": []
                  }

        for vin in tx['vin']:
            # handle first transaction that's the generated bitcoin from the network

            try:
                coinbase = vin['coinbase']
                result['sender'].append(('mining_reward', 0))
            except KeyError:
                # KeyError appears when vin['coinbase'] doesn't exit
                # following is common transaction between 2 bitcoin wallet

                # search for sender address
                sender_txid = vin['txid']
                sender_num = vin['vout']
                sender_tx = self.getrawtransaction(sender_txid, 1)
                for sender_vout in sender_tx['vout']:
                    if sender_vout['n'] == sender_num:
                        try:
                            result['sender'].append((sender_vout['scriptPubKey']['addresses'][0], sender_vout['value']))
                        except KeyError:
                            # Native segwit outputs (P2WSH and P2WPKH) do not currently have an address
                            # so there are no addresses for these outputs.
                            if sender_vout['scriptPubKey']['type'] in ['witness_v0_keyhash', 'witness_v0_scripthash']:
                                result['sender'].append(('Native_SegWit', sender_vout['value']))
                            elif sender_vout['scriptPubKey']['type'] in ['nonstandard', 'pubkey']:
                                result['sender'].append((sender_vout['scriptPubKey']['type'], sender_vout['value']))
                            else:
                                raise Exception('decoding sender impossible : %s', sender_tx)

        # association between sender, receiver and amount
        for vout in tx['vout']:
            value = vout['value']
            if value != 0.0:
                try:
                    receiver = vout['scriptPubKey']['addresses'][0]
                    btcscript = vout['scriptPubKey']['hex']
                    result['receiver'].append((receiver, value, btcscript))
                except KeyError:
                    # test if Native SegWit outputs
                    if vout['scriptPubKey']['type'] in ['witness_v0_keyhash', 'witness_v0_scripthash']:
                        # Native segwit outputs (P2WSH and P2WPKH) do not currently have an address type
                        # so there are no addresses for these outputs.
                        receiver = 'Native_SegWit'
                        btcscript = vout['scriptPubKey']['hex']
                        result['receiver'].append((receiver, value, btcscript))
                    elif vout['scriptPubKey']['type'] in ['nonstandard', 'pubkey']:
                        receiver = vout['scriptPubKey']['type']
                        btcscript = vout['scriptPubKey']['hex']
                        result['receiver'].append((receiver, value, btcscript))
                    # unknown error
                    else:
                        raise Exception('decoding receiver impossible : %s', tx)

        return result

    ####################
    # JSON-RPC METHODS #
    ####################

    # ressources :
    # * https://en.bitcoin.it/wiki/Original_Bitcoin_client/API_calls_list
    # * https://en.bitcoin.it/wiki/Elis-API
    # * http://chainquery.com/bitcoin-api

    def abandontransaction(self, txid):
        '''
        http://chainquery.com/bitcoin-api/abandontransaction

        NOT TESTED

        Mark in-wallet transaction <txid> as abandoned
        This will mark this transaction and all its in-wallet descendants as abandoned which will allow
        for their inputs to be respent.  It can be used to replace "stuck" or evicted transactions.
        It only works on transactions which are not included in a block and are not currently in the mempool.
        It has no effect on transactions which are already conflicted or abandoned.

        Arguments:
        1. "txid"    (string, required) The transaction id

        Result: Null
        '''
        return self.call('abandontransaction', [txid])

    def addmultisigaddress(self, nrequired, keys):
        '''
        http://chainquery.com/bitcoin-api/addmultisigaddress

        NOT TESTED

        Add a nrequired-to-sign multisignature address to the wallet.
        Each key is a Bitcoin address or hex-encoded public key.
        If 'account' is specified (DEPRECATED), assign address to that account.

        Arguments:
        1. nrequired        (numeric, required) The number of required signatures out of the n keys or addresses.
        2. "keys"         (string, required) A json array of bitcoin addresses or hex-encoded public keys
             [
               "address"  (string) bitcoin address or hex-encoded public key
               ...,
             ]
        3. "account"      (string, optional) DEPRECATED. An account to assign the addresses to.

        Result:
        "address"         (string) A bitcoin address associated with the keys.
        '''
        return self.call('addmultisigaddress'[nrequired, keys])

    def addnode(self, node, command):
        '''
        http://chainquery.com/bitcoin-api/addnode

        NOT TESTED

        Attempts to add or remove a node from the addnode list.
        Or try a connection to a node once.

        Arguments:
        1. "node"     (string, required) The node (see getpeerinfo for nodes)
        2. "command"  (string, required) 'add' to add a node to the list, 'remove' to remove a node from the list, 'onetry' to try a connection to the node once

        '''
        return self.call('addnode', [node, command])

    def createmultisig(self, nrequired, keys):
        '''
        http://chainquery.com/bitcoin-api/createmultisig

        NOT TESTED

        Creates a multi-signature address with n signature of m keys required.
        It returns a json object with the address and redeemScript.

        Arguments:
        1. nrequired      (numeric, required) The number of required signatures out of the n keys or addresses.
        2. "keys"       (string, required) A json array of keys which are bitcoin addresses or hex-encoded public keys
             [
               "key"    (string) bitcoin address or hex-encoded public key
               ,...
             ]

        Result:
        {
          "address":"multisigaddress",  (string) The value of the new multisig address.
          "redeemScript":"script"       (string) The string value of the hex-encoded redemption script.
        }
        '''
        return self.call('createmultisig', [nrequired, keys])

    def createrawtransaction(self, inputs, outputs, locktime=0, replaceable=False):
        '''
        http://chainquery.com/bitcoin-api/createrawtransaction

        NOT TESTED

        Create a transaction spending the given inputs and creating new outputs.
        Outputs can be addresses or data.
        Returns hex-encoded raw transaction.
        Note that the transaction's inputs are not signed, and
        it is not stored in the wallet or transmitted to the network.

        Arguments:
        1. "inputs"                (array, required) A json array of json objects
             [
               {
                 "txid":"id",    (string, required) The transaction id
                 "vout":n,         (numeric, required) The output number
                 "sequence":n      (numeric, optional) The sequence number
               }
               ,...
             ]
        2. "outputs"               (object, required) a json object with outputs
            {
              "address": x.xxx,    (numeric or string, required) The key is the bitcoin address, the numeric value (can be string) is the BTC amount
              "data": "hex"      (string, required) The key is "data", the value is hex encoded data
              ,...
            }
        3. locktime                  (numeric, optional, default=0) Raw locktime. Non-0 value also locktime-activates inputs
        4. replaceable               (boolean, optional, default=false) Marks this transaction as BIP125 replaceable.
                                     Allows this transaction to be replaced by a transaction with higher fees. If provided, it is an error if explicit sequence numbers are incompatible.

        Result:
        "transaction"              (string) hex string of the transaction
        '''
        return self.call('createrawtransaction', [inputs, outputs, locktime, replaceable])

    def decoderawtransaction(self, hexstring):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/decoderawtransaction

        Return a JSON object representing the serialized, hex-encoded transaction.

        Arguments:
        1. "hexstring"      (string, required) The transaction hex string

        Result:
        {
          "txid" : "id",        (string) The transaction id
          "hash" : "id",        (string) The transaction hash (differs from txid for witness transactions)
          "size" : n,             (numeric) The transaction size
          "vsize" : n,            (numeric) The virtual transaction size (differs from size for witness transactions)
          "version" : n,          (numeric) The version
          "locktime" : ttt,       (numeric) The lock time
          "vin" : [               (array of json objects)
             {
               "txid": "id",    (string) The transaction id
               "vout": n,         (numeric) The output number
               "scriptSig": {     (json object) The script
                 "asm": "asm",  (string) asm
                 "hex": "hex"   (string) hex
               },
               "txinwitness": ["hex", ...] (array of string) hex-encoded witness data (if any)
               "sequence": n     (numeric) The script sequence number
             }
             ,...
          ],
          "vout" : [             (array of json objects)
             {
               "value" : x.xxx,            (numeric) The value in BTC
               "n" : n,                    (numeric) index
               "scriptPubKey" : {          (json object)
                 "asm" : "asm",          (string) the asm
                 "hex" : "hex",          (string) the hex
                 "reqSigs" : n,            (numeric) The required sigs
                 "type" : "pubkeyhash",  (string) The type, eg 'pubkeyhash'
                 "addresses" : [           (json array of string)
                   "12tvKAXCxZjSmdNbao16dKXC8tRWfcF5oc"   (string) bitcoin address
                   ,...
                 ]
               }
             }
             ,...
          ],
        }
        '''
        return self.call('decoderawtransaction', [hexstring])

    def decodescript(self, hexstring):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/decodescript

        Decode a hex-encoded script.

        Arguments:
        1. "hexstring"     (string) the hex encoded script

        Result:
        {
          "asm":"asm",   (string) Script public key
          "hex":"hex",   (string) hex encoded public key
          "type":"type", (string) The output type
          "reqSigs": n,    (numeric) The required signatures
          "addresses": [   (json array of string)
             "address"     (string) bitcoin address
             ,...
          ],
          "p2sh","address" (string) address of P2SH script wrapping this redeem script (not returned if the script is already a P2SH).
        }
        '''
        return self.call('decodescript', [hexstring])

    def dumpprivkey(self, address):
        '''
        http://chainquery.com/bitcoin-api/dumpprivkey


        Reveals the private key corresponding to 'address'.
        Then the importprivkey can be used with this output

        Arguments:
        1. "address"   (string, required) The bitcoin address for the private key

        Result:
        "key"                (string) The private key
        '''
        return self.call('dumpprivkey', [address])

    def encryptwallet(self, passphrase):
        '''
        http://chainquery.com/bitcoin-api/encryptwallet

        Parameter #1—a passphrase - The passphrase to use for the encrypted wallet. Must be at least one character.
        Result—a notice (with program shutdown on success)

        '''
        return self.call('encryptwallet', [passphrase])

    def estimatefee(self, nblocks):
        '''
        http://chainquery.com/bitcoin-api/estimatefee

        DEPRECATED. Please use estimatesmartfee for more intelligent estimates.
        Estimates the approximate fee per kilobyte needed for a transaction to begin
        confirmation within nblocks blocks. Uses virtual transaction size of transaction
        as defined in BIP 141 (witness data is discounted).

        Arguments:
        1. nblocks     (numeric, required)

        Result:
        n              (numeric) estimated fee-per-kilobyte

        A negative value is returned if not enough transactions and blocks
        have been observed to make an estimate.
        -1 is always returned for nblocks == 1 as it is impossible to calculate
        a fee that is high enough to get reliably included in the next block.
        '''
        return self.call('estimatefee', [nblocks])

    def estimatepriority(self, number):
        '''
        http://chainquery.com/bitcoin-api/estimatepriority

        The estimatepriority RPC estimates the priority that a transaction needs in order to be included within a certain number of blocks as a free high-priority transaction. Transaction priority is relative to a transaction’s byte size.

        Parameter #1—how many blocks the transaction may wait before being included as a free high-priority transaction
        Result—the priority a transaction needs
        '''
        return self.call('estimatepriority', [number])

    def getaccountaddress(self, account):
        '''
        http://chainquery.com/bitcoin-api/getaccountaddress

        DEPRECATED. Returns the current Bitcoin address for receiving payments to this account.

        Arguments:
        1. "account"       (string, required) The account name for the address. It can also be set to the empty string "" to represent the default account. The account does not need to exist, it will be created and a new address created  if there is no account by the given name.

        Result:
        "address"          (string) The account bitcoin address

        '''
        return self.call('getaccountaddress', [account])

    def getaccount(self, address):
        '''
        http://chainquery.com/bitcoin-api/getaccount

        DEPRECATED. Returns the account associated with the given address.

        Arguments:
        1. "address"         (string, required) The bitcoin address for account lookup.

        Result:
        "accountname"        (string) the account address

        '''
        return self.call('getaccount', [address])

    def getaddednodeinfo(self, node):
        '''
        http://chainquery.com/bitcoin-api/getaddednodeinfo

        Returns information about the given added node, or all added nodes
        (note that onetry addnodes are not listed here)

        Arguments:
        1. "node"   (string, optional) If provided, return information about this specific node, otherwise all nodes are returned.

        Result:
        [
          {
            "addednode" : "192.168.0.201",   (string) The node IP address or name (as provided to addnode)
            "connected" : true|false,          (boolean) If connected
            "addresses" : [                    (list of objects) Only when connected = true
               {
                 "address" : "192.168.0.201:8333",  (string) The bitcoin server IP and port we're connected to
                 "connected" : "outbound"           (string) connection, inbound or outbound
               }
             ]
          }
          ,...
        ]

        '''
        return self.call('getaddednodeinfo', [node])

    def getaddressesbyaccount(self, account):
        '''
        http://chainquery.com/bitcoin-api/getaddressesbyaccount

        DEPRECATED. Returns the list of addresses for the given account.

        Arguments:
        1. "account"        (string, required) The account name.

        Result:
        [                     (json array of string)
          "address"         (string) a bitcoin address associated with the given account
          ,...
        ]
        '''
        return self.call('getaddressesbyaccount', [account])

    def getbalance(self, account="*", minconf=1, include_watchonly=False):
        '''
        http://chainquery.com/bitcoin-api/getbalance

        If account is not specified, returns the server's total available balance.
        If account is specified (DEPRECATED), returns the balance in the account.
        Note that the account "" is not the same as leaving the parameter out.
        The server total may be different to the balance in the default "" account.

        Arguments:
        1. "account"         (string, optional) DEPRECATED. The account string may be given as a
                             specific account name to find the balance associated with wallet keys in
                             a named account, or as the empty string ("") to find the balance
                             associated with wallet keys not in any named account, or as "*" to find
                             the balance associated with all wallet keys regardless of account.
                             When this option is specified, it calculates the balance in a different
                             way than when it is not specified, and which can count spends twice when
                             there are conflicting pending transactions (such as those created by
                             the bumpfee command), temporarily resulting in low or even negative
                             balances. In general, account balance calculation is not considered
                             reliable and has resulted in confusing outcomes, so it is recommended to
                             avoid passing this argument.
        2. minconf           (numeric, optional, default=1) Only include transactions confirmed at least this many times.
        3. include_watchonly (bool, optional, default=false) Also include balance in watch-only addresses (see 'importaddress')

        Result:
        amount              (numeric) The total amount in BTC received for this account.

        '''
        return self.call('getbalance', [account, minconf, include_watchonly])

    def getbestblockhash(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getbestblockhash

        Returns the hash of the best (tip) block in the longest blockchain.

        Result:
        "hex"      (string) the block hash hex encoded

        '''
        return self.call('getbestblockhash')

    def getblock(self, blockhash, verbosity=1):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getblock

        If verbosity is 0, returns a string that is serialized, hex-encoded data for block 'hash'.
        If verbosity is 1, returns an Object with information about block <hash>.
        If verbosity is 2, returns an Object with information about block <hash> and information about each transaction. 

        Arguments:
        1. "blockhash"          (string, required) The block hash
        2. verbosity              (numeric, optional, default=1) 0 for hex encoded data, 1 for a json object, and 2 for json object with transaction data

        Result (for verbosity = 0):
        "data"             (string) A string that is serialized, hex-encoded data for block 'hash'.

        Result (for verbosity = 1):
        {
          "hash" : "hash",     (string) the block hash (same as provided)
          "confirmations" : n,   (numeric) The number of confirmations, or -1 if the block is not on the main chain
          "size" : n,            (numeric) The block size
          "strippedsize" : n,    (numeric) The block size excluding witness data
          "weight" : n           (numeric) The block weight as defined in BIP 141
          "height" : n,          (numeric) The block height or index
          "version" : n,         (numeric) The block version
          "versionHex" : "00000000", (string) The block version formatted in hexadecimal
          "merkleroot" : "xxxx", (string) The merkle root
          "tx" : [               (array of string) The transaction ids
             "transactionid"     (string) The transaction id
             ,...
          ],
          "time" : ttt,          (numeric) The block time in seconds since epoch (Jan 1 1970 GMT)
          "mediantime" : ttt,    (numeric) The median block time in seconds since epoch (Jan 1 1970 GMT)
          "nonce" : n,           (numeric) The nonce
          "bits" : "1d00ffff", (string) The bits
          "difficulty" : x.xxx,  (numeric) The difficulty
          "chainwork" : "xxxx",  (string) Expected number of hashes required to produce the chain up to this block (in hex)
          "previousblockhash" : "hash",  (string) The hash of the previous block
          "nextblockhash" : "hash"       (string) The hash of the next block
        }

        Result (for verbosity = 2):
        {
          ...,                     Same output as verbosity = 1.
          "tx" : [               (array of Objects) The transactions in the format of the getrawtransaction RPC. Different from verbosity = 1 "tx" result.
                 ,...
          ],
          ,...                     Same output as verbosity = 1.
        }
        '''
        return self.call('getblock', [blockhash, verbosity])

    def getblockchaininfo(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getblockchaininfo

        Returns an object containing various state info regarding blockchain processing.

        Result:
        {
          "chain": "xxxx",        (string) current network name as defined in BIP70 (main, test, regtest)
          "blocks": xxxxxx,         (numeric) the current number of blocks processed in the server
          "headers": xxxxxx,        (numeric) the current number of headers we have validated
          "bestblockhash": "...", (string) the hash of the currently best block
          "difficulty": xxxxxx,     (numeric) the current difficulty
          "mediantime": xxxxxx,     (numeric) median time for the current best block
          "verificationprogress": xxxx, (numeric) estimate of verification progress [0..1]
          "chainwork": "xxxx"     (string) total amount of work in active chain, in hexadecimal
          "pruned": xx,             (boolean) if the blocks are subject to pruning
          "pruneheight": xxxxxx,    (numeric) lowest-height complete block stored
          "softforks": [            (array) status of softforks in progress
             {
                "id": "xxxx",        (string) name of softfork
                "version": xx,         (numeric) block version
                "reject": {            (object) progress toward rejecting pre-softfork blocks
                   "status": xx,       (boolean) true if threshold reached
                },
             }, ...
          ],
          "bip9_softforks": {          (object) status of BIP9 softforks in progress
             "xxxx" : {                (string) name of the softfork
                "status": "xxxx",    (string) one of "defined", "started", "locked_in", "active", "failed"
                "bit": xx,             (numeric) the bit (0-28) in the block version field used to signal this softfork (only for "started" status)
                "startTime": xx,       (numeric) the minimum median time past of a block at which the bit gains its meaning
                "timeout": xx,         (numeric) the median time past of a block at which the deployment is considered failed if not yet locked in
                "since": xx,           (numeric) height of the first block to which the status applies
                "statistics": {        (object) numeric statistics about BIP9 signalling for a softfork (only for "started" status)
                   "period": xx,       (numeric) the length in blocks of the BIP9 signalling period 
                   "threshold": xx,    (numeric) the number of blocks with the version bit set required to activate the feature 
                   "elapsed": xx,      (numeric) the number of blocks elapsed since the beginning of the current period 
                   "count": xx,        (numeric) the number of blocks with the version bit set in the current period 
                   "possible": xx      (boolean) returns false if there are not enough blocks left in this period to pass activation threshold 
                }
             }
          }
        }

        '''
        return self.call('getblockchaininfo')

    def getblockcount(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getblockcount

        Returns the number of blocks in the longest blockchain.

        Result:
        n    (numeric) The current block count


        '''
        return self.call('getblockcount')

    def getblockhash(self, height):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getblockhash

        Returns hash of block in best-block-chain at height provided.

        Arguments:
        1. height         (numeric, required) The height index

        Result:
        "hash"         (string) The block hash

        '''
        return self.call('getblockhash', [height])

    def getblocktemplate(self, template_request=None):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getblocktemplate

        If the request parameters include a 'mode' key, that is used to explicitly select between the default 'template' request or a 'proposal'.
        It returns data needed to construct a block to work on.
        For full specification, see BIPs 22, 23, 9, and 145:
            https://github.com/bitcoin/bips/blob/master/bip-0022.mediawiki
            https://github.com/bitcoin/bips/blob/master/bip-0023.mediawiki
            https://github.com/bitcoin/bips/blob/master/bip-0009.mediawiki#getblocktemplate_changes
            https://github.com/bitcoin/bips/blob/master/bip-0145.mediawiki

        Arguments:
        1. template_request         (json object, optional) A json object in the following spec
             {
               "mode":"template"    (string, optional) This must be set to "template", "proposal" (see BIP 23), or omitted
               "capabilities":[     (array, optional) A list of strings
                   "support"          (string) client side supported feature, 'longpoll', 'coinbasetxn', 'coinbasevalue', 'proposal', 'serverlist', 'workid'
                   ,...
               ],
               "rules":[            (array, optional) A list of strings
                   "support"          (string) client side supported softfork deployment
                   ,...
               ]
             }


        Result:
        {
          "version" : n,                    (numeric) The preferred block version
          "rules" : [ "rulename", ... ],    (array of strings) specific block rules that are to be enforced
          "vbavailable" : {                 (json object) set of pending, supported versionbit (BIP 9) softfork deployments
              "rulename" : bitnumber          (numeric) identifies the bit number as indicating acceptance and readiness for the named softfork rule
              ,...
          },
          "vbrequired" : n,                 (numeric) bit mask of versionbits the server requires set in submissions
          "previousblockhash" : "xxxx",     (string) The hash of current highest block
          "transactions" : [                (array) contents of non-coinbase transactions that should be included in the next block
              {
                 "data" : "xxxx",             (string) transaction data encoded in hexadecimal (byte-for-byte)
                 "txid" : "xxxx",             (string) transaction id encoded in little-endian hexadecimal
                 "hash" : "xxxx",             (string) hash encoded in little-endian hexadecimal (including witness data)
                 "depends" : [                (array) array of numbers
                     n                          (numeric) transactions before this one (by 1-based index in 'transactions' list) that must be present in the final block if this one is
                     ,...
                 ],
                 "fee": n,                    (numeric) difference in value between transaction inputs and outputs (in Satoshis); for coinbase transactions, this is a negative Number of the total collected block fees (ie, not including the block subsidy); if key is not present, fee is unknown and clients MUST NOT assume there isn't one
                 "sigops" : n,                (numeric) total SigOps cost, as counted for purposes of block limits; if key is not present, sigop cost is unknown and clients MUST NOT assume it is zero
                 "weight" : n,                (numeric) total transaction weight, as counted for purposes of block limits
                 "required" : true|false      (boolean) if provided and true, this transaction must be in the final block
              }
              ,...
          ],
          "coinbaseaux" : {                 (json object) data that should be included in the coinbase's scriptSig content
              "flags" : "xx"                  (string) key name is to be ignored, and value included in scriptSig
          },
          "coinbasevalue" : n,              (numeric) maximum allowable input to coinbase transaction, including the generation award and transaction fees (in Satoshis)
          "coinbasetxn" : { ... },          (json object) information for coinbase transaction
          "target" : "xxxx",                (string) The hash target
          "mintime" : xxx,                  (numeric) The minimum timestamp appropriate for next block time in seconds since epoch (Jan 1 1970 GMT)
          "mutable" : [                     (array of string) list of ways the block template may be changed 
             "value"                          (string) A way the block template may be changed, e.g. 'time', 'transactions', 'prevblock'
             ,...
          ],
          "noncerange" : "00000000ffffffff",(string) A range of valid nonces
          "sigoplimit" : n,                 (numeric) limit of sigops in blocks
          "sizelimit" : n,                  (numeric) limit of block size
          "weightlimit" : n,                (numeric) limit of block weight
          "curtime" : ttt,                  (numeric) current timestamp in seconds since epoch (Jan 1 1970 GMT)
          "bits" : "xxxxxxxx",              (string) compressed target of next block
          "height" : n                      (numeric) The height of the next block
        }

        '''
        if template_request is None:
            return self.call('getblocktemplate', [template_request])
        else:
            return self.call('getblocktemplate')

    def getchaintips(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getchaintips

        Return information about all known tips in the block tree, including the main chain as well as orphaned branches.

        Result:
        [
          {
            "height": xxxx,         (numeric) height of the chain tip
            "hash": "xxxx",         (string) block hash of the tip
            "branchlen": 0          (numeric) zero for main chain
            "status": "active"      (string) "active" for the main chain
          },
          {
            "height": xxxx,
            "hash": "xxxx",
            "branchlen": 1          (numeric) length of branch connecting the tip to the main chain
            "status": "xxxx"        (string) status of the chain (active, valid-fork, valid-headers, headers-only, invalid)
          }
        ]
        Possible values for status:
        1.  "invalid"               This branch contains at least one invalid block
        2.  "headers-only"          Not all blocks for this branch are available, but the headers are valid
        3.  "valid-headers"         All blocks are available for this branch, but they were never fully validated
        4.  "valid-fork"            This branch is not part of the active chain, but is fully validated
        5.  "active"                This is the tip of the active main chain, which is certainly valid

        '''
        return self.call('getchaintips')

    def getconnectioncount(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getconnectioncount


        Returns the number of connections to other nodes.

        Result:
        n          (numeric) The connection count

        '''
        return self.call('getconnectioncount')

    def getdifficulty(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getdifficulty

        Returns the proof-of-work difficulty as a multiple of the minimum difficulty.

        Result:
        n.nnn       (numeric) the proof-of-work difficulty as a multiple of the minimum difficulty.

        '''
        return self.call('getdifficulty')

    def getgenerate(self):
        '''
        http://chainquery.com/bitcoin-api/getgenerate

        The getgenerate RPC returns true if the node is set to generate blocks using its CPU.

        Parameters: none
        Result—whether the server is set to generate blocks

        '''
        return self.call('getgenerate')

    def getinfo(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getinfo

        DEPRECATED. Returns an object containing various state info.

        Result:
        {
          "deprecation-warning": "..." (string) warning that the getinfo command is deprecated and will be removed in 0.16
          "version": xxxxx,           (numeric) the server version
          "protocolversion": xxxxx,   (numeric) the protocol version
          "walletversion": xxxxx,     (numeric) the wallet version
          "balance": xxxxxxx,         (numeric) the total bitcoin balance of the wallet
          "blocks": xxxxxx,           (numeric) the current number of blocks processed in the server
          "timeoffset": xxxxx,        (numeric) the time offset
          "connections": xxxxx,       (numeric) the number of connections
          "proxy": "host:port",       (string, optional) the proxy used by the server
          "difficulty": xxxxxx,       (numeric) the current difficulty
          "testnet": true|false,      (boolean) if the server is using testnet or not
          "keypoololdest": xxxxxx,    (numeric) the timestamp (seconds since Unix epoch) of the oldest pre-generated key in the key pool
          "keypoolsize": xxxx,        (numeric) how many new keys are pre-generated
          "unlocked_until": ttt,      (numeric) the timestamp in seconds since epoch (midnight Jan 1 1970 GMT) that the wallet is unlocked for transfers, or 0 if the wallet is locked
          "paytxfee": x.xxxx,         (numeric) the transaction fee set in BTC/kB
          "relayfee": x.xxxx,         (numeric) minimum relay fee for transactions in BTC/kB
          "errors": "..."             (string) any error messages
        }

        '''
        return self.call('getinfo')

    def getmempoolinfo(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getmempoolinfo

        Returns details on the active state of the TX memory pool.

        Result:
        {
          "size": xxxxx,               (numeric) Current tx count
          "bytes": xxxxx,              (numeric) Sum of all virtual transaction sizes as defined in BIP 141. Differs from actual serialized size because witness data is discounted
          "usage": xxxxx,              (numeric) Total memory usage for the mempool
          "maxmempool": xxxxx,         (numeric) Maximum memory usage for the mempool
          "mempoolminfee": xxxxx       (numeric) Minimum feerate (BTC per KB) for tx to be accepted
        }

        '''
        return self.call('getmempoolinfo')

    def getmininginfo(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getmininginfo

        Returns a json object containing mining-related information.
        Result:
        {
          "blocks": nnn,             (numeric) The current block
          "currentblockweight": nnn, (numeric) The last block weight
          "currentblocktx": nnn,     (numeric) The last block transaction
          "difficulty": xxx.xxxxx    (numeric) The current difficulty
          "errors": "..."            (string) Current errors
          "networkhashps": nnn,      (numeric) The network hashes per second
          "pooledtx": n              (numeric) The size of the mempool
          "chain": "xxxx",           (string) current network name as defined in BIP70 (main, test, regtest)
        }

        '''
        return self.call('getmininginfo')

    def getnettotals(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getnettotals

        Returns information about network traffic, including bytes in, bytes out,
        and current time.

        Result:
        {
          "totalbytesrecv": n,   (numeric) Total bytes received
          "totalbytessent": n,   (numeric) Total bytes sent
          "timemillis": t,       (numeric) Current UNIX time in milliseconds
          "uploadtarget":
          {
            "timeframe": n,                         (numeric) Length of the measuring timeframe in seconds
            "target": n,                            (numeric) Target in bytes
            "target_reached": true|false,           (boolean) True if target is reached
            "serve_historical_blocks": true|false,  (boolean) True if serving historical blocks
            "bytes_left_in_cycle": t,               (numeric) Bytes left in current time cycle
            "time_left_in_cycle": t                 (numeric) Seconds left in current time cycle
          }
        }

        '''
        return self.call('getnettotals')

    def getnetworkhashps(self, nblocks=120, height=-1):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getnetworkhashps

        Returns the estimated network hashes per second based on the last n blocks.
        Pass in [blocks] to override # of blocks, -1 specifies since last difficulty change.
        Pass in [height] to estimate the network speed at the time when a certain block was found.

        Arguments:
        1. nblocks     (numeric, optional, default=120) The number of blocks, or -1 for blocks since last difficulty change.
        2. height      (numeric, optional, default=-1) To estimate at the time of the given height.

        Result:
        x             (numeric) Hashes per second estimated

        '''
        return self.call('getnetworkhashps', [nblocks, height])

    def getnetworkinfo(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getnetworkinfo

        Returns an object containing various state info regarding P2P networking.

        Result:
        {
          "version": xxxxx,                      (numeric) the server version
          "subversion": "/Satoshi:x.x.x/",     (string) the server subversion string
          "protocolversion": xxxxx,              (numeric) the protocol version
          "localservices": "xxxxxxxxxxxxxxxx", (string) the services we offer to the network
          "localrelay": true|false,              (bool) true if transaction relay is requested from peers
          "timeoffset": xxxxx,                   (numeric) the time offset
          "connections": xxxxx,                  (numeric) the number of connections
          "networkactive": true|false,           (bool) whether p2p networking is enabled
          "networks": [                          (array) information per network
          {
            "name": "xxx",                     (string) network (ipv4, ipv6 or onion)
            "limited": true|false,               (boolean) is the network limited using -onlynet?
            "reachable": true|false,             (boolean) is the network reachable?
            "proxy": "host:port"               (string) the proxy that is used for this network, or empty if none
            "proxy_randomize_credentials": true|false,  (string) Whether randomized credentials are used
          }
          ,...
          ],
          "relayfee": x.xxxxxxxx,                (numeric) minimum relay fee for transactions in BTC/kB
          "incrementalfee": x.xxxxxxxx,          (numeric) minimum fee increment for mempool limiting or BIP 125 replacement in BTC/kB
          "localaddresses": [                    (array) list of local addresses
          {
            "address": "xxxx",                 (string) network address
            "port": xxx,                         (numeric) network port
            "score": xxx                         (numeric) relative score
          }
          ,...
          ]
          "warnings": "..."                    (string) any network warnings
        }

        '''
        return self.call('getnetworkinfo')

    def getpeerinfo(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getpeerinfo

        Returns data about each connected network node as a json array of objects.

        Result:
        [
          {
            "id": n,                   (numeric) Peer index
            "addr":"host:port",      (string) The IP address and port of the peer
            "addrbind":"ip:port",    (string) Bind address of the connection to the peer
            "addrlocal":"ip:port",   (string) Local address as reported by the peer
            "services":"xxxxxxxxxxxxxxxx",   (string) The services offered
            "relaytxes":true|false,    (boolean) Whether peer has asked us to relay transactions to it
            "lastsend": ttt,           (numeric) The time in seconds since epoch (Jan 1 1970 GMT) of the last send
            "lastrecv": ttt,           (numeric) The time in seconds since epoch (Jan 1 1970 GMT) of the last receive
            "bytessent": n,            (numeric) The total bytes sent
            "bytesrecv": n,            (numeric) The total bytes received
            "conntime": ttt,           (numeric) The connection time in seconds since epoch (Jan 1 1970 GMT)
            "timeoffset": ttt,         (numeric) The time offset in seconds
            "pingtime": n,             (numeric) ping time (if available)
            "minping": n,              (numeric) minimum observed ping time (if any at all)
            "pingwait": n,             (numeric) ping wait (if non-zero)
            "version": v,              (numeric) The peer version, such as 7001
            "subver": "/Satoshi:0.8.5/",  (string) The string version
            "inbound": true|false,     (boolean) Inbound (true) or Outbound (false)
            "addnode": true|false,     (boolean) Whether connection was due to addnode and is using an addnode slot
            "startingheight": n,       (numeric) The starting height (block) of the peer
            "banscore": n,             (numeric) The ban score
            "synced_headers": n,       (numeric) The last header we have in common with this peer
            "synced_blocks": n,        (numeric) The last block we have in common with this peer
            "inflight": [
               n,                        (numeric) The heights of blocks we're currently asking from this peer
               ...
            ],
            "whitelisted": true|false, (boolean) Whether the peer is whitelisted
            "bytessent_per_msg": {
               "addr": n,              (numeric) The total bytes sent aggregated by message type
               ...
            },
            "bytesrecv_per_msg": {
               "addr": n,              (numeric) The total bytes received aggregated by message type
               ...
            }
          }
          ,...
        ]

        '''
        return self.call('getpeerinfo')

    def getrawmempool(self, verbose=False):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getrawmempool

        Returns all transaction ids in memory pool as a json array of string transaction ids.

        Hint: use getmempoolentry to fetch a specific transaction from the mempool.

        Arguments:
        1. verbose (boolean, optional, default=false) True for a json object, false for array of transaction ids

        Result: (for verbose = false):
        [                     (json array of string)
          "transactionid"     (string) The transaction id
          ,...
        ]

        Result: (for verbose = true):
        {                           (json object)
          "transactionid" : {       (json object)
            "size" : n,             (numeric) virtual transaction size as defined in BIP 141. This is different from actual serialized size for witness transactions as witness data is discounted.
            "fee" : n,              (numeric) transaction fee in BTC
            "modifiedfee" : n,      (numeric) transaction fee with fee deltas used for mining priority
            "time" : n,             (numeric) local time transaction entered pool in seconds since 1 Jan 1970 GMT
            "height" : n,           (numeric) block height when transaction entered pool
            "descendantcount" : n,  (numeric) number of in-mempool descendant transactions (including this one)
            "descendantsize" : n,   (numeric) virtual transaction size of in-mempool descendants (including this one)
            "descendantfees" : n,   (numeric) modified fees (see above) of in-mempool descendants (including this one)
            "ancestorcount" : n,    (numeric) number of in-mempool ancestor transactions (including this one)
            "ancestorsize" : n,     (numeric) virtual transaction size of in-mempool ancestors (including this one)
            "ancestorfees" : n,     (numeric) modified fees (see above) of in-mempool ancestors (including this one)
            "depends" : [           (array) unconfirmed transactions used as inputs for this transaction
                "transactionid",    (string) parent transaction id
               ... ]
          }, ...
        }

        '''
        return self.call('getrawmempool', [verbose])

    def getrawtransaction(self, txid, verbose=False):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getrawtransaction

        NOTE: By default this function only works for mempool transactions. If the -txindex option is
        enabled, it also works for blockchain transactions.
        DEPRECATED: for now, it also works for transactions with unspent outputs.

        Return the raw transaction data.

        If verbose is 'true', returns an Object with information about 'txid'.
        If verbose is 'false' or omitted, returns a string that is serialized, hex-encoded data for 'txid'.

        Arguments:
        1. "txid"      (string, required) The transaction id
        2. verbose       (bool, optional, default=false) If false, return a string, otherwise return a json object

        Result (if verbose is not set or set to false):
        "data"      (string) The serialized, hex-encoded data for 'txid'

        Result (if verbose is set to true):
        {
          "hex" : "data",       (string) The serialized, hex-encoded data for 'txid'
          "txid" : "id",        (string) The transaction id (same as provided)
          "hash" : "id",        (string) The transaction hash (differs from txid for witness transactions)
          "size" : n,             (numeric) The serialized transaction size
          "vsize" : n,            (numeric) The virtual transaction size (differs from size for witness transactions)
          "version" : n,          (numeric) The version
          "locktime" : ttt,       (numeric) The lock time
          "vin" : [               (array of json objects)
             {
               "txid": "id",    (string) The transaction id
               "vout": n,         (numeric)
               "scriptSig": {     (json object) The script
                 "asm": "asm",  (string) asm
                 "hex": "hex"   (string) hex
               },
               "sequence": n      (numeric) The script sequence number
               "txinwitness": ["hex", ...] (array of string) hex-encoded witness data (if any)
             }
             ,...
          ],
          "vout" : [              (array of json objects)
             {
               "value" : x.xxx,            (numeric) The value in BTC
               "n" : n,                    (numeric) index
               "scriptPubKey" : {          (json object)
                 "asm" : "asm",          (string) the asm
                 "hex" : "hex",          (string) the hex
                 "reqSigs" : n,            (numeric) The required sigs
                 "type" : "pubkeyhash",  (string) The type, eg 'pubkeyhash'
                 "addresses" : [           (json array of string)
                   "address"        (string) bitcoin address
                   ,...
                 ]
               }
             }
             ,...
          ],
          "blockhash" : "hash",   (string) the block hash
          "confirmations" : n,      (numeric) The confirmations
          "time" : ttt,             (numeric) The transaction time in seconds since epoch (Jan 1 1970 GMT)
          "blocktime" : ttt         (numeric) The block time in seconds since epoch (Jan 1 1970 GMT)
        }

        '''
        return self.call('getrawtransaction', [txid, verbose])

    def getreceivedbyaccount(self, account, minconf=1):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getreceivedbyaccount

        DEPRECATED. Returns the total amount received by addresses with <account> in transactions with at least [minconf] confirmations.

        Arguments:
        1. "account"      (string, required) The selected account, may be the default account using "".
        2. minconf          (numeric, optional, default=1) Only include transactions confirmed at least this many times.

        Result:
        amount              (numeric) The total amount in BTC received for this account.

        '''
        return self.call('getreceivedbyaccount', [account, minconf])

    def getreceivedbyaddress(self, address, minconf=1):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getreceivedbyaddress

        Returns the total amount received by the given address in transactions with at least minconf confirmations.

        Arguments:
        1. "address"         (string, required) The bitcoin address for transactions.
        2. minconf             (numeric, optional, default=1) Only include transactions confirmed at least this many times.

        Result:
        amount   (numeric) The total amount in BTC received at this address.

        '''
        return self.call('getreceivedbyaddress', [address, minconf])

    def gettransaction(self, txid, include_watchonly=False):
        '''
        http://chainquery.com/bitcoin-api/gettransaction

        Get detailed information about in-wallet transaction <txid>

        Arguments:
        1. "txid"                  (string, required) The transaction id
        2. "include_watchonly"     (bool, optional, default=false) Whether to include watch-only addresses in balance calculation and details[]

        Result:
        {
          "amount" : x.xxx,        (numeric) The transaction amount in BTC
          "fee": x.xxx,            (numeric) The amount of the fee in BTC. This is negative and only available for the 
                                      'send' category of transactions.
          "confirmations" : n,     (numeric) The number of confirmations
          "blockhash" : "hash",  (string) The block hash
          "blockindex" : xx,       (numeric) The index of the transaction in the block that includes it
          "blocktime" : ttt,       (numeric) The time in seconds since epoch (1 Jan 1970 GMT)
          "txid" : "transactionid",   (string) The transaction id.
          "time" : ttt,            (numeric) The transaction time in seconds since epoch (1 Jan 1970 GMT)
          "timereceived" : ttt,    (numeric) The time received in seconds since epoch (1 Jan 1970 GMT)
          "bip125-replaceable": "yes|no|unknown",  (string) Whether this transaction could be replaced due to BIP125 (replace-by-fee);
                                                           may be unknown for unconfirmed transactions not in the mempool
          "details" : [
            {
              "account" : "accountname",      (string) DEPRECATED. The account name involved in the transaction, can be "" for the default account.
              "address" : "address",          (string) The bitcoin address involved in the transaction
              "category" : "send|receive",    (string) The category, either 'send' or 'receive'
              "amount" : x.xxx,                 (numeric) The amount in BTC
              "label" : "label",              (string) A comment for the address/transaction, if any
              "vout" : n,                       (numeric) the vout value
              "fee": x.xxx,                     (numeric) The amount of the fee in BTC. This is negative and only available for the 
                                                   'send' category of transactions.
              "abandoned": xxx                  (bool) 'true' if the transaction has been abandoned (inputs are respendable). Only available for the 
                                                   'send' category of transactions.
            }
            ,...
          ],
          "hex" : "data"         (string) Raw data for transaction
        }

        '''
        return self.call('gettransaction', [txid, include_watchonly])

    def gettxout(self, txid, n, include_mempool=True):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/gettxout

        Returns details about an unspent transaction output.

        Arguments:
        1. "txid"             (string, required) The transaction id
        2. "n"                (numeric, required) vout number
        3. "include_mempool"  (boolean, optional) Whether to include the mempool. Default: true.     Note that an unspent output that is spent in the mempool won't appear.

        Result:
        {
          "bestblock" : "hash",    (string) the block hash
          "confirmations" : n,       (numeric) The number of confirmations
          "value" : x.xxx,           (numeric) The transaction value in BTC
          "scriptPubKey" : {         (json object)
             "asm" : "code",       (string)
             "hex" : "hex",        (string)
             "reqSigs" : n,          (numeric) Number of required signatures
             "type" : "pubkeyhash", (string) The type, eg pubkeyhash
             "addresses" : [          (array of string) array of bitcoin addresses
                "address"     (string) bitcoin address
                ,...
             ]
          },
          "coinbase" : true|false   (boolean) Coinbase or not
        }
        '''
        return self.call('gettxout', [txid, n, include_mempool])

    def gettxoutproof(self, txids, blockhash=None):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/gettxoutproof

        Returns a hex-encoded proof that "txid" was included in a block.

        NOTE: By default this function only works sometimes. This is when there is an
        unspent output in the utxo for this transaction. To make it always work,
        you need to maintain a transaction index, using the -txindex command line option or
        specify the block in which the transaction is included manually (by blockhash).

        Arguments:
        1. "txids"       (string) A json array of txids to filter
            [
              "txid"     (string) A transaction hash
              ,...
            ]
        2. "blockhash"   (string, optional) If specified, looks for txid in the block with this hash

        Result:
        "data"           (string) A string that is a serialized, hex-encoded data for the proof.

        '''
        if blockhash is None:
            return self.call('gettxoutproof', [txids])
        else:
            return self.call('gettxoutproof', [txids, blockhash])

    def getunconfirmedbalance(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getunconfirmedbalance

        Returns the server's total unconfirmed balance
        '''
        return self.call('getunconfirmedbalance')

    def getwalletinfo(self):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/getwalletinfo

        Returns an object containing various wallet state info.

        Result:
        {
          "walletname": xxxxx,             (string) the wallet name
          "walletversion": xxxxx,          (numeric) the wallet version
          "balance": xxxxxxx,              (numeric) the total confirmed balance of the wallet in BTC
          "unconfirmed_balance": xxx,      (numeric) the total unconfirmed balance of the wallet in BTC
          "immature_balance": xxxxxx,      (numeric) the total immature balance of the wallet in BTC
          "txcount": xxxxxxx,              (numeric) the total number of transactions in the wallet
          "keypoololdest": xxxxxx,         (numeric) the timestamp (seconds since Unix epoch) of the oldest pre-generated key in the key pool
          "keypoolsize": xxxx,             (numeric) how many new keys are pre-generated (only counts external keys)
          "keypoolsize_hd_internal": xxxx, (numeric) how many new keys are pre-generated for internal use (used for change outputs, only appears if the wallet is using this feature, otherwise external keys are used)
          "unlocked_until": ttt,           (numeric) the timestamp in seconds since epoch (midnight Jan 1 1970 GMT) that the wallet is unlocked for transfers, or 0 if the wallet is locked
          "paytxfee": x.xxxx,              (numeric) the transaction fee configuration, set in BTC/kB
          "hdmasterkeyid": "<hash160>"     (string) the Hash160 of the HD master pubkey
        }

        '''
        return self.call('getwalletinfo')

    def help(self, command=None):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/help

        List all commands, or get help for a specified command.

        Arguments:
        1. "command"     (string, optional) The command to get help on

        Result:
        "text"     (string) The help text

        '''
        if command is None:
            return self.call('help')
        else:
            return self.call('help', [command])

    def keypoolrefill(self, newsize=100):
        '''

        SEEM TO WORK (no RPC error)

        http://chainquery.com/bitcoin-api/keypoolrefill

        Fills the keypool.
        Requires wallet passphrase to be set with walletpassphrase call.

        Arguments
        1. newsize     (numeric, optional, default=100) The new keypool size

        '''
        return self.call('keypoolrefill', [newsize])

    def listaccounts(self, minconf=1, include_watchonly=False):
        '''
        http://chainquery.com/bitcoin-api/listaccounts


        SEEM TO WORK (no RPC error)

        DEPRECATED. Returns Object that has account names as keys, account balances as values.

        Arguments:
        1. minconf             (numeric, optional, default=1) Only include transactions with at least this many confirmations
        2. include_watchonly   (bool, optional, default=false) Include balances in watch-only addresses (see 'importaddress')

        Result:
        {                      (json object where keys are account names, and values are numeric balances
          "account": x.xxx,  (numeric) The property name is the account name, and the value is the total balance for the account.
          ...
        }

        '''
        return self.call('listaccounts', [minconf, include_watchonly])

    def listaddressgroupings(self):
        '''
        http://chainquery.com/bitcoin-api/listaddressgroupings


        SEEM TO WORK (no RPC error)

        Lists groups of addresses which have had their common ownership
        made public by common use as inputs or as the resulting change
        in past transactions

        Result:
        [
          [
            [
              "address",            (string) The bitcoin address
              amount,                 (numeric) The amount in BTC
              "account"             (string, optional) DEPRECATED. The account
            ]
            ,...
          ]
          ,...
        ]
        '''
        return self.call('listaddressgroupings')

    def listlockunspent(self):
        '''
        http://chainquery.com/bitcoin-api/listlockunspent


        SEEM TO WORK (no RPC error)

        Returns list of temporarily unspendable outputs.
        See the lockunspent call to lock and unlock transactions for spending.

        Result:
        [
          {
            "txid" : "transactionid",     (string) The transaction id locked
            "vout" : n                      (numeric) The vout value
          }
          ,...
        ]

        '''
        return self.call('listlockunspent')

    def listreceivedbyaccount(self, minconf=1, include_empty=False, include_watchonly=False):
        '''
        http://chainquery.com/bitcoin-api/listreceivedbyaccount


        SEEM TO WORK (no RPC error)

        DEPRECATED. List balances by account.

        Arguments:
        1. minconf           (numeric, optional, default=1) The minimum number of confirmations before payments are included.
        2. include_empty     (bool, optional, default=false) Whether to include accounts that haven't received any payments.
        3. include_watchonly (bool, optional, default=false) Whether to include watch-only addresses (see 'importaddress').

        Result:
        [
          {
            "involvesWatchonly" : true,   (bool) Only returned if imported addresses were involved in transaction
            "account" : "accountname",  (string) The account name of the receiving account
            "amount" : x.xxx,             (numeric) The total amount received by addresses with this account
            "confirmations" : n,          (numeric) The number of confirmations of the most recent transaction included
            "label" : "label"           (string) A comment for the address/transaction, if any
          }
          ,...
        ]
        '''
        return self.call('listreceivedbyaccount', [minconf, include_empty, include_watchonly])

    def listreceivedbyaddress(self, minconf=1, include_empty=False, include_watchonly=False):
        '''
        http://chainquery.com/bitcoin-api/listreceivedbyaddress


        SEEM TO WORK (no RPC error)

        List balances by receiving address.

        Arguments:
        1. minconf           (numeric, optional, default=1) The minimum number of confirmations before payments are included.
        2. include_empty     (bool, optional, default=false) Whether to include addresses that haven't received any payments.
        3. include_watchonly (bool, optional, default=false) Whether to include watch-only addresses (see 'importaddress').

        Result:
        [
          {
            "involvesWatchonly" : true,        (bool) Only returned if imported addresses were involved in transaction
            "address" : "receivingaddress",  (string) The receiving address
            "account" : "accountname",       (string) DEPRECATED. The account of the receiving address. The default account is "".
            "amount" : x.xxx,                  (numeric) The total amount in BTC received by the address
            "confirmations" : n,               (numeric) The number of confirmations of the most recent transaction included
            "label" : "label",               (string) A comment for the address/transaction, if any
            "txids": [
               n,                                (numeric) The ids of transactions received with the address 
               ...
            ]
          }
          ,...
        ]
        '''
        return self.call('listreceivedbyaddress', [minconf, include_empty, include_watchonly])

    def listtransactions(self, account="*", count=10, skip=0, include_watchonly=False):
        '''
        http://chainquery.com/bitcoin-api/listtransactions


        SEEM TO WORK (no RPC error)

        Returns up to 'count' most recent transactions skipping the first 'from' transactions for account 'account'.

        Arguments:
        1. "account"    (string, optional) DEPRECATED. The account name. Should be "*".
        2. count          (numeric, optional, default=10) The number of transactions to return
        3. skip           (numeric, optional, default=0) The number of transactions to skip
        4. include_watchonly (bool, optional, default=false) Include transactions to watch-only addresses (see 'importaddress')

        Result:
        [
          {
            "account":"accountname",       (string) DEPRECATED. The account name associated with the transaction. 
                                                        It will be "" for the default account.
            "address":"address",    (string) The bitcoin address of the transaction. Not present for 
                                                        move transactions (category = move).
            "category":"send|receive|move", (string) The transaction category. 'move' is a local (off blockchain)
                                                        transaction between accounts, and not associated with an address,
                                                        transaction id or block. 'send' and 'receive' transactions are 
                                                        associated with an address, transaction id and block details
            "amount": x.xxx,          (numeric) The amount in BTC. This is negative for the 'send' category, and for the
                                                 'move' category for moves outbound. It is positive for the 'receive' category,
                                                 and for the 'move' category for inbound funds.
            "label": "label",       (string) A comment for the address/transaction, if any
            "vout": n,                (numeric) the vout value
            "fee": x.xxx,             (numeric) The amount of the fee in BTC. This is negative and only available for the 
                                                 'send' category of transactions.
            "confirmations": n,       (numeric) The number of confirmations for the transaction. Available for 'send' and 
                                                 'receive' category of transactions. Negative confirmations indicate the
                                                 transaction conflicts with the block chain
            "trusted": xxx,           (bool) Whether we consider the outputs of this unconfirmed transaction safe to spend.
            "blockhash": "hashvalue", (string) The block hash containing the transaction. Available for 'send' and 'receive'
                                                  category of transactions.
            "blockindex": n,          (numeric) The index of the transaction in the block that includes it. Available for 'send' and 'receive'
                                                  category of transactions.
            "blocktime": xxx,         (numeric) The block time in seconds since epoch (1 Jan 1970 GMT).
            "txid": "transactionid", (string) The transaction id. Available for 'send' and 'receive' category of transactions.
            "time": xxx,              (numeric) The transaction time in seconds since epoch (midnight Jan 1 1970 GMT).
            "timereceived": xxx,      (numeric) The time received in seconds since epoch (midnight Jan 1 1970 GMT). Available 
                                                  for 'send' and 'receive' category of transactions.
            "comment": "...",       (string) If a comment is associated with the transaction.
            "otheraccount": "accountname",  (string) DEPRECATED. For the 'move' category of transactions, the account the funds came 
                                                  from (for receiving funds, positive amounts), or went to (for sending funds,
                                                  negative amounts).
            "bip125-replaceable": "yes|no|unknown",  (string) Whether this transaction could be replaced due to BIP125 (replace-by-fee);
                                                             may be unknown for unconfirmed transactions not in the mempool
            "abandoned": xxx          (bool) 'true' if the transaction has been abandoned (inputs are respendable). Only available for the 
                                                 'send' category of transactions.
          }
        ]

        '''
        return self.call('listtransactions', [account, count, skip, include_watchonly])

    def listunspent(self, minconf=1, maxconf=9999999, addresses=[], include_unsafe=True, query_options={}):
        '''
        http://chainquery.com/bitcoin-api/listunspent

        SEEM TO WORK (no RPC error)

        Returns array of unspent transaction outputs
        with between minconf and maxconf (inclusive) confirmations.
        Optionally filter to only include txouts paid to specified addresses.

        Arguments:
        1. minconf          (numeric, optional, default=1) The minimum confirmations to filter
        2. maxconf          (numeric, optional, default=9999999) The maximum confirmations to filter
        3. "addresses"      (string) A json array of bitcoin addresses to filter
            [
              "address"     (string) bitcoin address
              ,...
            ]
        4. include_unsafe (bool, optional, default=true) Include outputs that are not safe to spend
                          See description of "safe" attribute below.
        5. query_options    (json, optional) JSON with query options
            {
              "minimumAmount"    (numeric or string, default=0) Minimum value of each UTXO in BTC
              "maximumAmount"    (numeric or string, default=unlimited) Maximum value of each UTXO in BTC
              "maximumCount"     (numeric or string, default=unlimited) Maximum number of UTXOs
              "minimumSumAmount" (numeric or string, default=unlimited) Minimum sum value of all UTXOs in BTC
            }

        Result
        [                   (array of json object)
          {
            "txid" : "txid",          (string) the transaction id
            "vout" : n,               (numeric) the vout value
            "address" : "address",    (string) the bitcoin address
            "account" : "account",    (string) DEPRECATED. The associated account, or "" for the default account
            "scriptPubKey" : "key",   (string) the script key
            "amount" : x.xxx,         (numeric) the transaction output amount in BTC
            "confirmations" : n,      (numeric) The number of confirmations
            "redeemScript" : n        (string) The redeemScript if scriptPubKey is P2SH
            "spendable" : xxx,        (bool) Whether we have the private keys to spend this output
            "solvable" : xxx,         (bool) Whether we know how to spend this output, ignoring the lack of keys
            "safe" : xxx              (bool) Whether this output is considered safe to spend. Unconfirmed transactions
                                      from outside keys and unconfirmed replacement transactions are considered unsafe
                                      and are not eligible for spending by fundrawtransaction and sendtoaddress.
          }
          ,...
        ]
        '''
        return self.call('listunspent', [minconf, maxconf, addresses, include_unsafe, query_options])

    def lockunspent(self, unlock, transactions=None):
        '''

        TESTED

        http://chainquery.com/bitcoin-api/lockunspent

        Updates list of temporarily unspendable outputs.
        Temporarily lock (unlock=false) or unlock (unlock=true) specified transaction outputs.
        If no transaction outputs are specified when unlocking then all current locked transaction outputs are unlocked.
        A locked transaction output will not be chosen by automatic coin selection, when spending bitcoins.
        Locks are stored in memory only. Nodes start with zero locked outputs, and the locked output list
        is always cleared (by virtue of process exit) when a node stops or fails.
        Also see the listunspent call

        Arguments:
        1. unlock            (boolean, required) Whether to unlock (true) or lock (false) the specified transactions
        2. "transactions"  (string, optional) A json array of objects. Each object the txid (string) vout (numeric)
             [           (json array of json objects)
               {
                 "txid":"id",    (string) The transaction id
                 "vout": n         (numeric) The output number
               }
               ,...
             ]

        Result:
        true|false    (boolean) Whether the command was successful or not

        '''
        if transactions is None:
            return self.call('lockunspent', [unlock])
        else:
            return self.call('lockunspent', [unlock, transactions])

    def prioritisetransaction(self, txid, fee_delta):
        '''
        http://chainquery.com/bitcoin-api/prioritisetransaction

        NOT TESTED

        Accepts the transaction into mined blocks at a higher (or lower) priority

        Arguments:
        1. "txid"       (string, required) The transaction id.
        2. dummy          (numeric, optional) API-Compatibility for previous API. Must be zero or null.
                          DEPRECATED. For forward compatibility use named arguments and omit this parameter.
        3. fee_delta      (numeric, required) The fee value (in satoshis) to add (or subtract, if negative).
                          The fee is not actually paid, only the algorithm for selecting transactions into a block
                          considers the transaction as it would have paid a higher (or lower) fee.

        Result:
        true              (boolean) Returns true

        '''
        return self.call('prioritisetransaction', [txid, fee_delta])

    def sendfrom(self, fromaccount, toaddress, amount, minconf=1, comment=None, comment_to=None):
        '''
        http://chainquery.com/bitcoin-api/sendfrom

        NOT TESTED

        DEPRECATED (use sendtoaddress). Sent an amount from an account to a bitcoin address.
        Requires wallet passphrase to be set with walletpassphrase call.

        Arguments:
        1. "fromaccount"       (string, required) The name of the account to send funds from. May be the default account using "".
                               Specifying an account does not influence coin selection, but it does associate the newly created
                               transaction with the account, so the account's balance computation and transaction history can reflect
                               the spend.
        2. "toaddress"         (string, required) The bitcoin address to send funds to.
        3. amount                (numeric or string, required) The amount in BTC (transaction fee is added on top).
        4. minconf               (numeric, optional, default=1) Only use funds with at least this many confirmations.
        5. "comment"           (string, optional) A comment used to store what the transaction is for. 
                                             This is not part of the transaction, just kept in your wallet.
        6. "comment_to"        (string, optional) An optional comment to store the name of the person or organization 
                                             to which you're sending the transaction. This is not part of the transaction, 
                                             it is just kept in your wallet.

        Result:
        "txid"                 (string) The transaction id.

        '''
        param = [fromaccount, toaddress, amount]
        if comment is not None:
            param.append(comment)
        if comment_to is not None:
            param.append(comment_to)
        return self.call('sendfrom', param)

    def sendmany(self, fromaccount, amounts, minconf=1, comment=None, subtractfeefrom=None, replaceable=None, conf_target=None, estimate_mode="UNSET"):
        '''
        http://chainquery.com/bitcoin-api/sendmany

        NOT TESTED

        Send multiple times. Amounts are double-precision floating point numbers.
        Requires wallet passphrase to be set with walletpassphrase call.

        Arguments:
        1. "fromaccount"         (string, required) DEPRECATED. The account to send the funds from. Should be "" for the default account
        2. "amounts"             (string, required) A json object with addresses and amounts
            {
              "address":amount   (numeric or string) The bitcoin address is the key, the numeric amount (can be string) in BTC is the value
              ,...
            }
        3. minconf                 (numeric, optional, default=1) Only use the balance confirmed at least this many times.
        4. "comment"             (string, optional) A comment
        5. subtractfeefrom         (array, optional) A json array with addresses.
                                   The fee will be equally deducted from the amount of each selected address.
                                   Those recipients will receive less bitcoins than you enter in their corresponding amount field.
                                   If no addresses are specified here, the sender pays the fee.
            [
              "address"          (string) Subtract fee from this address
              ,...
            ]
        6. replaceable            (boolean, optional) Allow this transaction to be replaced by a transaction with higher fees via BIP 125
        7. conf_target            (numeric, optional) Confirmation target (in blocks)
        8. "estimate_mode"      (string, optional, default=UNSET) The fee estimate mode, must be one of:
               "UNSET"
               "ECONOMICAL"
               "CONSERVATIVE"

        Result:
        "txid"                   (string) The transaction id for the send. Only 1 transaction is created regardless of 
                                            the number of addresses.

        '''
        param = [fromaccount, amounts, minconf]
        if comment is not None:
            param.append(comment)
        if subtractfeefrom is not None:
            param.append(subtractfeefrom)
        if replaceable is not None:
            param.append(replaceable)
        if conf_target is not None:
            param.append(conf_target)
        param.append(estimate_mode)
        return self.call('sendmany', param)

    def sendrawtransaction(self, hexstring, allowhighfees=False):
        '''
        http://chainquery.com/bitcoin-api/sendrawtransaction

        NOT TESTED

        Submits raw transaction (serialized, hex-encoded) to local node and network.

        Also see createrawtransaction and signrawtransaction calls.

        Arguments:
        1. "hexstring"    (string, required) The hex string of the raw transaction)
        2. allowhighfees    (boolean, optional, default=false) Allow high fees

        Result:
        "hex"             (string) The transaction hash in hex

        '''
        return self.call('sendrawtransaction', [hexstring, allowhighfees])

    def sendtoaddress(self, address, amount, comment=None, comment_to=None, subtractfeefromamount=False, replaceable=None, estimate_mode="UNSET"):
        '''
        http://chainquery.com/bitcoin-api/sendtoaddress

        NOT TESTED

        Send an amount to a given address.

        Requires wallet passphrase to be set with walletpassphrase call.
        Arguments:
        1. "address"            (string, required) The bitcoin address to send to.
        2. "amount"             (numeric or string, required) The amount in BTC to send. eg 0.1
        3. "comment"            (string, optional) A comment used to store what the transaction is for. 
                                     This is not part of the transaction, just kept in your wallet.
        4. "comment_to"         (string, optional) A comment to store the name of the person or organization 
                                     to which you're sending the transaction. This is not part of the 
                                     transaction, just kept in your wallet.
        5. subtractfeefromamount  (boolean, optional, default=false) The fee will be deducted from the amount being sent.
                                     The recipient will receive less bitcoins than you enter in the amount field.
        6. replaceable            (boolean, optional) Allow this transaction to be replaced by a transaction with higher fees via BIP 125
        7. conf_target            (numeric, optional) Confirmation target (in blocks)
        8. "estimate_mode"      (string, optional, default=UNSET) The fee estimate mode, must be one of:
               "UNSET"
               "ECONOMICAL"
               "CONSERVATIVE"

        Result:
        "txid"                  (string) The transaction id.

        '''
        param = [address, amount]
        if comment is not None:
            param.append(comment)
        if comment_to is not None:
            param.append(comment_to)
        param.append(subtractfeefromamount)
        if replaceable is not None:
            param.append(replaceable)
        param.append(estimate_mode)
        return self.call('sendtoaddress', param)

    def settxfee(self, amount):
        '''
        http://chainquery.com/bitcoin-api/settxfee

        SEEM TO WORK (no RPC error)

        Set the transaction fee per kB. Overwrites the paytxfee parameter.

        Arguments:
        1. amount         (numeric or string, required) The transaction fee in BTC/kB

        Result
        true|false        (boolean) Returns true if successful

        '''
        return self.call('settxfee', [amount])

    def signmessage(self, address, message):
        '''
        http://chainquery.com/bitcoin-api/signmessage

        NOT TESTED

        Sign a message with the private key of an address
        Requires wallet passphrase to be set with walletpassphrase call.

        Arguments:
        1. "address"         (string, required) The bitcoin address to use for the private key.
        2. "message"         (string, required) The message to create a signature of.

        Result:
        "signature"          (string) The signature of the message encoded in base 64

        '''
        return self.call('signmessage', [address, message])

    def signrawtransaction(self, hexstring, prevtxs=None, privkeys=None, sighashtype="ALL"):
        '''
        http://chainquery.com/bitcoin-api/signrawtransaction

        NOT TESTED

        Sign inputs for raw transaction (serialized, hex-encoded).
        The second optional argument (may be null) is an array of previous transaction outputs that
        this transaction depends on but may not yet be in the block chain.
        The third optional argument (may be null) is an array of base58-encoded private
        keys that, if given, will be the only keys used to sign the transaction.

        Requires wallet passphrase to be set with walletpassphrase call.

        Arguments:
        1. "hexstring"     (string, required) The transaction hex string
        2. "prevtxs"       (string, optional) An json array of previous dependent transaction outputs
             [               (json array of json objects, or 'null' if none provided)
               {
                 "txid":"id",             (string, required) The transaction id
                 "vout":n,                  (numeric, required) The output number
                 "scriptPubKey": "hex",   (string, required) script key
                 "redeemScript": "hex",   (string, required for P2SH or P2WSH) redeem script
                 "amount": value            (numeric, required) The amount spent
               }
               ,...
            ]
        3. "privkeys"     (string, optional) A json array of base58-encoded private keys for signing
            [                  (json array of strings, or 'null' if none provided)
              "privatekey"   (string) private key in base58-encoding
              ,...
            ]
        4. "sighashtype"     (string, optional, default=ALL) The signature hash type. Must be one of
               "ALL"
               "NONE"
               "SINGLE"
               "ALL|ANYONECANPAY"
               "NONE|ANYONECANPAY"
               "SINGLE|ANYONECANPAY"

        Result:
        {
          "hex" : "value",           (string) The hex-encoded raw transaction with signature(s)
          "complete" : true|false,   (boolean) If the transaction has a complete set of signatures
          "errors" : [                 (json array of objects) Script verification errors (if there are any)
            {
              "txid" : "hash",           (string) The hash of the referenced, previous transaction
              "vout" : n,                (numeric) The index of the output to spent and used as input
              "scriptSig" : "hex",       (string) The hex-encoded signature script
              "sequence" : n,            (numeric) Script sequence number
              "error" : "text"           (string) Verification or signing error related to the input
            }
            ,...
          ]
        }

        '''
        param = [hexstring]
        if prevtxs is not None:
            param.append(prevtxs)
        if privkeys is not None:
            param.append(privkeys)
        param.append(sighashtype)
        return self.call('signrawtransaction', param)

    def submitblock(self, hexdata, dummy=None):
        '''
        http://chainquery.com/bitcoin-api/submitblock

        NOT TESTED

        Attempts to submit new block to network.
        See https://en.bitcoin.it/wiki/BIP_0022 for full specification.

        Arguments
        1. "hexdata"        (string, required) the hex-encoded block data to submit
        2. "dummy"          (optional) dummy value, for compatibility with BIP22. This value is ignored.

        Result: None

        '''
        if dummy is None:
            return self.call('submitblock', [hexdata])
        else:
            return self.call('submitblock', [hexdata, dummy])

    def validateaddress(self, address):
        '''
        http://chainquery.com/bitcoin-api/validateaddress

        TESTED

        Return information about the given bitcoin address.

        Arguments:
        1. "address"     (string, required) The bitcoin address to validate

        Result:
        {
          "isvalid" : true|false,       (boolean) If the address is valid or not. If not, this is the only property returned.
          "address" : "address", (string) The bitcoin address validated
          "scriptPubKey" : "hex",       (string) The hex encoded scriptPubKey generated by the address
          "ismine" : true|false,        (boolean) If the address is yours or not
          "iswatchonly" : true|false,   (boolean) If the address is watchonly
          "isscript" : true|false,      (boolean) If the key is a script
          "script" : "type"             (string, optional) The output script type. Possible types: nonstandard, pubkey, pubkeyhash, scripthash, multisig, nulldata, witness_v0_keyhash, witness_v0_scripthash
          "hex" : "hex",                (string, optional) The redeemscript for the p2sh address
          "addresses"                   (string, optional) Array of addresses associated with the known redeemscript
            [
              "address"
              ,...
            ]
          "sigsrequired" : xxxxx        (numeric, optional) Number of signatures required to spend multisig output
          "pubkey" : "publickeyhex",    (string) The hex value of the raw public key
          "iscompressed" : true|false,  (boolean) If the address is compressed
          "account" : "account"         (string) DEPRECATED. The account associated with the address, "" is the default account
          "timestamp" : timestamp,        (number, optional) The creation time of the key if available in seconds since epoch (Jan 1 1970 GMT)
          "hdkeypath" : "keypath"       (string, optional) The HD keypath if the key is HD and available
          "hdmasterkeyid" : "<hash160>" (string, optional) The Hash160 of the HD master pubkey
        }

        '''
        return self.call('validateaddress', [address])

    def verifymessage(self, address, signature, message):
        '''
        http://chainquery.com/bitcoin-api/verifymessage

        NOT TESTED

        Verify a signed message

        Arguments:
        1. "address"         (string, required) The bitcoin address to use for the signature.
        2. "signature"       (string, required) The signature provided by the signer in base 64 encoding (see signmessage).
        3. "message"         (string, required) The message that was signed.

        Result:
        true|false   (boolean) If the signature is verified or not.

        '''
        return self.call('verifymessage', [address, signature, message])

    def verifytxoutproof(self, proof):
        '''
        http://chainquery.com/bitcoin-api/verifytxoutproof

        TESTED

        Verifies that a proof points to a transaction in a block, returning the transaction it commits to
        and throwing an RPC error if the block is not in our best chain

        Arguments:
        1. "proof"    (string, required) The hex-encoded proof generated by gettxoutproof

        Result:
        ["txid"]      (array, strings) The txid(s) which the proof commits to, or empty array if the proof is invalid

        '''
        return self.call('verifytxoutproof', [proof])

    def walletlock(self):
        '''
        http://chainquery.com/bitcoin-api/walletlock

        NOT TESTED

        Parameters: none
        Result—null on success

        Removes the wallet encryption key from memory, locking the wallet.
        After calling this method, you will need to call walletpassphrase again
        before being able to call any methods which require the wallet to be unlocked.

        '''
        return self.call('walletlock')

    def walletpassphrase(self, passphrase, timeout):
        '''
        http://chainquery.com/bitcoin-api/walletpassphrase

        NOT TESTED

        Stores the wallet decryption key in memory for 'timeout' seconds.
        This is needed prior to performing transactions related to private keys such as sending bitcoins

        Arguments:
        1. "passphrase"     (string, required) The wallet passphrase
        2. timeout            (numeric, required) The time to keep the decryption key in seconds.

        Note:
        Issuing the walletpassphrase command while the wallet is already unlocked will set a new unlock
        time that overrides the old one.

        '''
        return self.call('walletpassphrase', [passphrase, timeout])

    def walletpassphrasechange(self, oldpassphrase, newpassphrase):
        '''
        http://chainquery.com/bitcoin-api/walletpassphrasechange

        NOT TESTED

        Changes the wallet passphrase from 'oldpassphrase' to 'newpassphrase'.

        Arguments:
        1. "oldpassphrase"      (string) The current passphrase
        2. "newpassphrase"      (string) The new passphrase

        '''
        return self.call('walletpassphrasechange', [oldpassphrase, newpassphrase])


class BitcoinBitcoreExplorerRPC(BitcoinExplorerRPC):
    '''
    BitcoinExplorerRPC subclass for bitcored-specific methods

    new RPC calls : https://bitcore.io/guides/bitcoin
    '''

    def __init__(self, host):
        BitcoinExplorerRPC.__init__(self, host=host)

    def getaddresstxids(self):
        raise NotImplementedError

    def getblock(self, blockhash, verbosity=True):
        return self.call('getblock', [blockhash, verbosity])

    def __script_pub_key_to_bech32(self, script):
        # remove OP_0 + len(pubkeyhash)
        pubkeyhash = script[4:]
        if script[2:4] == '14':
            type_tx = 'witness_v0_keyhash'
        elif script[2:4] == '20':
            type_tx = 'witness_v0_scripthash'
        else:
            raise Exception('script = %s', script)

        # bc for mainnet
        # 0x00 for the version = v0
        # pubkeyhash
        # return bech32 address
        return bech32_encode('bc', 0x00,
                             binascii.unhexlify(pubkeyhash)), type_tx

    # case TX_NONSTANDARD: return "nonstandard";
    # case TX_PUBKEY: return "pubkey";
    # case TX_PUBKEYHASH: return "pubkeyhash";
    # case TX_SCRIPTHASH: return "scripthash";
    # case TX_MULTISIG: return "multisig";
    # case TX_NULL_DATA: return "nulldata";
    # case TX_WITNESS_V0_KEYHASH: return "witness_v0_keyhash";
    # case TX_WITNESS_V0_SCRIPTHASH: return "witness_v0_scripthash";
    # case TX_WITNESS_UNKNOWN: return "witness_unknown";

    # decode_tx to use extra fields add by bitcore in new getrawtransaction
    def decode_tx(self, tx):

        result = {"txid": tx['txid'],
                  "sender": [],
                  "receiver": [],
                  "total_value_input": 0.0,
                  "total_value_output": 0.0,
                  "fee": 0.0
                  }

        # get the senders
        for vin in tx['vin']:

            # test for commons transaction first
            # vin['address'] & vin['addr'] are bitcore specific
            if 'address' in vin:
                sender_address = vin['address']
                type_tx = 'standard'
            elif 'addr' in vin:
                sender_address = vin['addr']
                type_tx = 'standard'

            # coinbase transaction
            # only one per block
            # first transaction that's the coinbase mining reward
            elif 'coinbase' in vin:
                result['sender'].append(('mining_reward', 0,
                                         '', 'mining_reward'))
                break

            # SegWit or less classic case
            # need to retrieve complete input transaction
            else:
                sender_tx = self.getrawtransaction(vin['txid'], 1)
                for sender_vout in sender_tx['vout']:
                    if sender_vout['n'] == vin['vout']:
                        script_pub_key = sender_vout['scriptPubKey']
                        script_sig = script_pub_key['hex']
                        # pubkey
                        try:
                            sender_address = script_pub_key['addresses'][0]
                            type_tx = script_pub_key['type']
                            print('sender type_tx: %s' % type_tx)
                        # SegWit
                        except KeyError:
                            sender_address, type_tx = \
                                self.__script_pub_key_to_bech32(script_sig)
                            if sender_address is None:
                                raise Exception('sender bech32 : %s',
                                                script_sig)

            sender_value = vin['value']
            sender_script = vin['scriptSig']['hex']
            result['sender'].append((sender_address, sender_value,
                                     sender_script, type_tx))

        # get the receivers
        for vout in tx['vout']:
            value = vout['value']
            script_pub_key = vout['scriptPubKey']
            btcscript = script_pub_key['hex']

            try:
                receiver = script_pub_key['addresses'][0]
                type_tx = script_pub_key['type']
            # KeyError appears when vin['address'] doesn't exit
            # means we have SegWit transaction
            except KeyError:
                if 'type' in script_pub_key:
                    type_tx = script_pub_key['type']
                    if type_tx == 'nulldata':
                        receiver = 'lost_bitcoin'
                    else:
                        #print('receiver type_tx: %s' % type_tx)
                        receiver, type_tx = \
                            self.__script_pub_key_to_bech32(btcscript)
                        if receiver is None:
                            raise Exception('receiver bech32 : %s', script_sig)

            result['receiver'].append((receiver, value, btcscript, type_tx))

        total_in = sum(v for _, v, _, _ in result['sender'])
        total_out = sum(v for _, v, _, _ in result['receiver'])

        for s, v, _, _ in result['sender']:
            if s == '':
                print('TXID = %s' % tx['txid'])

        for r, v, _, _ in result['receiver']:
            if r == '':
                print('TXID = %s' % tx['txid'])

        result["total_value_input"] = total_in
        result["total_value_output"] = total_out
        result["fee"] = total_in - total_out if total_in - total_out > 0 else 0
        return result

# example address p2wsh
# txid = a388d6f88373aacf2a5c170eeff4adf51f2c6744da26375d5890f42d653a2e6c
# txid2 = 37138d3df8e1d41bf6474ecdc21d53f78ab9907c500172de31bda4048556bd83
# pubkeyhash = 701a8d401c84fb13e6baf169d59684e17abd9fa216c8cc5b9fc63d622ff8c58
# address = bc1qwqdg6squsna38e46795at95yu9atm8azzmyvckulcc7kytlcckxswvvzej

# example address p2wpkh
# txid = fa3c4931c3f31eda18df255d754aa8f36a514f6ef7408d963912c47bb5cc5ec7
# txid2 = 761619410d9f2a7fa69336583a0351dd86caf9ed2cee8765132a93caa44f77de
# pubkeyhash = f2c78dda8d18a90545045942989406bf90966f7f
# address = bc1q7trcmk5drz5s23gyt9pf39qxh7gfvmmlr8kc2n

# can cause crash
# 0fcb06da0fb13e112fe68f3d674dc1366ec2930b4852ad8581b8ef7cc5f25fdf
# a562429d601b5559b9e1d732d7ad7c6071243f9b260af3f480757353841321ed

# first tx SegWit
# txid = f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd
# block_number = 481824
