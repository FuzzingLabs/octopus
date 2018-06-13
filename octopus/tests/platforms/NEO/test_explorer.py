from octopus.platforms.NEO.explorer import NeoExplorerRPC

import unittest


class NeoExplorerTestCase(unittest.TestCase):

    explorer = NeoExplorerRPC()

    wallet_address = "AJBENSwajTzQtwyJFkiJSv7MAaaMc7DsRz"
    asset_id = "c56f33fc6ecfcd0c225c4ab356fee59390af8560be0e930faebe74a6daff7c9b"
    block_hash = "0x881da7e14680cd4a020aa503dc602a92a411ad3184b6b14789074c775fbe5b7b"
    block_number = 1917115
    contract_hash = "d3cce84d0800172d09c88ccad61130611bd047a4"
    tx_id = 'f4250dab094c38d8265acc15c366dc508d2e14bf5699e12d9df26577ed74d657'
    contract_hash2 = "ecc6b20d3ccac1ee9ef109af5a7cdb85706b1df9"

    def testRPCCommand(self):

        #######################
        # HIGHT-LEVEL METHODS #
        #######################

        self.assertEqual(len(self.explorer.get_transaction(self.tx_id, False)), 524)
        self.assertEqual(self.explorer.get_block_by_hash(self.block_hash)['index'], self.block_number)
        self.assertEqual(self.explorer.get_block_by_number(self.block_number)['hash'], self.block_hash)

        ####################
        # JSON-RPC METHODS #
        ####################

        self.assertEqual(len(self.explorer.getaccountstate(self.wallet_address)), 5)
        self.assertEqual(len(self.explorer.getassetstate(self.asset_id)), 12)
        self.assertEqual(len(self.explorer.getbestblockhash()), 66)
        self.assertEqual(self.explorer.getblock(self.block_hash)['index'], self.block_number)
        self.assertEqual(self.explorer.getblock(self.block_number)['hash'], self.block_hash)
        self.assertEqual(type(self.explorer.getblockcount()), int)
        self.assertEqual(self.explorer.getblockhash(self.block_number), self.block_hash)
        self.assertEqual(self.explorer.getblocksysfee(self.block_number), '206594')
        self.assertEqual(type(self.explorer.getconnectioncount()), int)
        self.assertEqual(len(self.explorer.getcontractstate(self.contract_hash)), 11)
        self.assertEqual(type(self.explorer.getrawmempool()), list)
        self.assertEqual(len(self.explorer.getrawtransaction(self.tx_id, False)), 524)
        self.assertEqual(type(self.explorer.invoke(self.contract_hash, [{"type": "String","value": "name"}])), dict)
        self.assertEqual(type(self.explorer.invokefunction(self.contract_hash2, "balanceOf", [{"type": "Hash160", "value": "bfc469dd56932409677278f6b7422f3e1f34481d"}])), dict)
        self.assertEqual(type(self.explorer.invokescript("00046e616d656711c4d1f4fba619f2628870d36e3a9773e874705b")), dict)
        self.assertEqual(self.explorer.validateaddress(self.wallet_address)['isvalid'], True)

        # Not tested
        '''
        dumpprivkey
        getapplicationlog
        getbalance
        getnewaddress
        getstorage
        gettxout
        getpeers
        getversion
        listaddress
        sendrawtransaction
        sendtoaddress
        sendmany
        '''

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(NeoExplorerTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
