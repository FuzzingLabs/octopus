from octopus.platforms.BTC.explorer import BitcoinExplorerRPC
from octopus.platforms.BTC.explorer import RPC_USER, RPC_PASSWORD, RPC_HOST

import unittest


class BitcoinExplorerTestCase(unittest.TestCase):

    explorer = BitcoinExplorerRPC(host=('%s:%s@%s' % (RPC_USER, RPC_PASSWORD, RPC_HOST)))

    blockhash = '00000000000000000024fb37364cbf81fd49cc2d51c09c75c35433c3a1945d04'
    txid = '1b5bfc2681d40c872126919ccb1752de4cca42dcfc594899f2ef11db4b05bb39'
    tx_raw = '0200000001686b654b40737f0daa1532f64e525dc925e60d075403d38cfb12ac9097764015040000006a473044022009ec3f26984906a813faae05d968ec06bf1c68883e09a00b6333126ea87d96b302201cf1d2b9165442aa178fdf772a3909c3d2ba69e454eb8660fa35df8645e3bcb60121022f2caec3ad2f3b174d048a0d46f4f6e8ba4e9d02f6bdbba64ac6817f7ac6c131ffffffff02060d0700000000001976a91407c5acae3abc91735a1471e275e33abbffada89088ac00581300000000001976a91432f2e30111e1dc45f415430ef082cb64225c538a88ac00000000'
    wallet_address = '15wDxrRCn7YiCXdvqjcih6G8svrmq5AQSS'
    script_hex = "76a82096b3fe1f4ec8fd076379267f72443bed81cc49c18a2913f7e1f0727f6f9f4fbf88ac"
    script_asm = 'OP_DUP OP_SHA256 96b3fe1f4ec8fd076379267f72443bed81cc49c18a2913f7e1f0727f6f9f4fbf OP_EQUALVERIFY OP_CHECKSIG'

    def testRPCCommand(self):

        #######################
        # HIGHT-LEVEL METHODS #
        #######################

        self.assertEqual(self.explorer.get_transaction(self.txid, 0), self.tx_raw)
        self.assertEqual(len(self.explorer.get_block_by_hash(self.blockhash)), 18)
        self.assertEqual(len(self.explorer.get_block_by_number(500000)), 18)

        ####################
        # JSON-RPC METHODS #
        ####################

        self.assertEqual(self.explorer.decoderawtransaction(self.tx_raw)['txid'], self.txid)
        self.assertEqual(self.explorer.decodescript(self.script_hex)['asm'], self.script_asm)
        self.assertEqual(len(self.explorer.getbestblockhash()), len(self.blockhash))
        self.assertEqual(len(self.explorer.getblock(self.blockhash)), 18)
        self.assertEqual(len(self.explorer.getblockchaininfo()), 11)
        self.assertEqual(type(self.explorer.getblockcount()), int)
        self.assertEqual(self.explorer.getblockhash(500000), self.blockhash)
        # self.assertEqual(len(self.explorer.getchaintips()), 2)
        self.assertEqual(type(self.explorer.getconnectioncount()), int)
        self.assertEqual(type(self.explorer.getdifficulty()), float)
        self.assertEqual(len(self.explorer.getinfo()), 16)
        self.assertEqual(len(self.explorer.getmempoolinfo()), 5)
        self.assertEqual(len(self.explorer.getmininginfo()), 8)
        self.assertEqual(len(self.explorer.getnettotals()), 4)
        self.assertEqual(type(self.explorer.getnetworkhashps()), float)
        self.assertEqual(len(self.explorer.getnetworkinfo()), 13)
        self.assertEqual(len(self.explorer.getpeerinfo()), 8)
        self.assertEqual(type(self.explorer.getrawmempool()), list)
        self.assertEqual(self.explorer.getrawtransaction(self.txid), self.tx_raw)
        self.assertEqual(type(self.explorer.getreceivedbyaccount('')), float)
        self.assertEqual(type(self.explorer.getreceivedbyaddress(self.wallet_address)), float)
        self.assertEqual(len(self.explorer.gettxout(self.txid, 0)), 5)
        self.assertEqual(len(self.explorer.gettxoutproof([self.txid])), 818)
        self.assertEqual(type(self.explorer.getunconfirmedbalance()), float)
        self.assertEqual(len(self.explorer.getwalletinfo()), 9)
        self.assertEqual(type(self.explorer.help()), str)
        self.assertEqual(len(self.explorer.validateaddress(self.wallet_address)), 6)
        self.assertEqual(self.explorer.verifytxoutproof(self.explorer.gettxoutproof([self.txid])), [self.txid])

        # Not tested
        '''
        self.explorer.abandontransaction()
        self.explorer.addmultisigaddress()
        self.explorer.addnode()
        self.explorer.createmultisig()
        self.explorer.createrawtransaction()
        self.explorer.dumpprivkey()
        self.explorer.encryptwallet()
        self.explorer.estimatefee()
        self.explorer.estimatepriority()
        self.explorer.getaccountaddress()
        self.explorer.getaccount()
        self.explorer.getaddednodeinfo()
        self.explorer.getaddressesbyaccount()
        self.explorer.getbalance()
        self.explorer.gettransaction()
        self.explorer.keypoolrefill()
        self.explorer.listaccounts()
        self.explorer.listaddressgroupings()
        self.explorer.listlockunspent()
        self.explorer.listreceivedbyaccount()
        self.explorer.listreceivedbyaddress()
        self.explorer.listtransactions()
        self.explorer.listunspent()
        self.explorer.lockunspent()
        self.explorer.prioritisetransaction()
        self.explorer.sendfrom()
        self.explorer.sendmany()
        self.explorer.sendrawtransaction()
        self.explorer.sendtoaddress()
        self.explorer.settxfee()
        self.explorer.signmessage()
        self.explorer.signrawtransaction()
        self.explorer.submitblock()

        self.explorer.verifymessage()
        self.explorer.walletlock()
        self.explorer.walletpassphrase()
        self.explorer.walletpassphrasechange()
        '''

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BitcoinExplorerTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
