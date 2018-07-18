from octopus.platforms.ETH.explorer import EthereumInfuraExplorer

import unittest


class EthereumExplorerTestCase(unittest.TestCase):

    # please only used this key for octopus - Infura registration is FREE
    explorer = EthereumInfuraExplorer("bHuaQhX91nkQBac8Wtgj")

    '''TODO'''
    block_number = 5100196
    block_hash = '0x98a548cbd0cd385f46c9bf28c16bc36dc6ec27207617e236f527716e617ae91b'
    contract_address = '0xBB9bc244D798123fDe783fCc1C72d3Bb8C189413'
    address = "0x956b6B7454884b734B29A8115F045a95179ea00C"
    tx_hash = '0x345303843c2f3041d12f0c5e6075fd294c2e2ca8cd9b4a9addca3f8caf4380ff'

    def testRPCCommand(self):

        #######################
        # HIGHT-LEVEL METHODS #
        #######################

        self.assertEqual(self.explorer.get_transaction(self.tx_hash), self.explorer.eth_getTransactionByHash(self.tx_hash))
        self.assertEqual(len(self.explorer.get_block_by_hash(self.block_hash)), 20)
        self.assertEqual(len(self.explorer.get_block_by_number(self.block_number)), 20)

        ####################
        # JSON-RPC METHODS #
        ####################

        self.assertEqual(type(self.explorer.web3_clientVersion()), str)
        self.assertEqual(type(self.explorer.web3_sha3('0x' + b'hello world'.hex())), str)
        self.assertEqual(type(self.explorer.net_version()), str)
        self.assertEqual(type(self.explorer.net_listening()), bool)
        self.assertEqual(type(self.explorer.net_peerCount()), int)
        self.assertEqual(type(self.explorer.eth_protocolVersion()), str)
        self.assertEqual(type(self.explorer.eth_syncing()), bool)
        self.assertEqual(type(self.explorer.eth_mining()), bool)
        self.assertEqual(type(self.explorer.eth_hashrate()), int)
        self.assertEqual(type(self.explorer.eth_gasPrice()), int)
        self.assertEqual(type(self.explorer.eth_accounts()), list)
        self.assertEqual(type(self.explorer.eth_blockNumber()), int)
        self.assertEqual(type(self.explorer.eth_getBalance(self.address)), int)
        self.assertEqual(type(self.explorer.eth_getStorageAt("0x295a70b2de5e3953354a6a8344e616ed314d7251", 0, "latest")), str)
        self.assertEqual(type(self.explorer.eth_getTransactionCount(self.address)), int)

        self.assertEqual(self.explorer.eth_getBlockTransactionCountByHash(self.block_hash), 69)
        self.assertEqual(self.explorer.eth_getBlockTransactionCountByNumber(self.block_number), 69)
        self.assertEqual(self.explorer.eth_getUncleCountByBlockHash(self.block_hash), 0)
        self.assertEqual(self.explorer.eth_getUncleCountByBlockNumber(self.block_number), 0)

        self.assertEqual(len(self.explorer.eth_getCode(self.contract_address)), 21678)
        self.assertEqual(len(self.explorer.eth_getBlockByHash(self.block_hash)), 20)
        self.assertEqual(len(self.explorer.eth_getBlockByNumber(self.block_number)), 20)

        self.assertEqual(len(self.explorer.eth_getTransactionByHash(self.tx_hash)), 14)
        self.assertEqual(len(self.explorer.eth_getTransactionByBlockNumberAndIndex(self.block_number, 1)), 14)

        self.assertEqual(len(self.explorer.eth_getTransactionReceipt('0xf02ffa405bae96e62a9e36fbd781362ca378ec62353d5e2bd0585868d3deaf61')), 12)
        # self.assertEqual(type(self.explorer.eth_newBlockFilter()), str)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(EthereumExplorerTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
