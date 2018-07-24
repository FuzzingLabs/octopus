#
# Title: Retrieve ETHereum wasm smart contract bytecode
#        using InfuraExplorer on KOVAN network
# Date: 07/24/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.platforms.ETH.explorer import EthereumInfuraExplorer
from octopus.platforms.ETH.explorer import INFURA_KOVAN

# connection to ROPSTEN network (testnet)
explorer = EthereumInfuraExplorer("bHuaQhX91nkQBac8Wtgj",
                                  network=INFURA_KOVAN)
# connection to MAINNET network (mainnet)
# explorer = EthereumInfuraExplorer("bHuaQhX91nkQBac8Wtgj")

# test infura access
block_number = explorer.eth_blockNumber()
print('blockNumber = %d' % block_number)

# retrieve code of this smart contract
addr = "0x1120e596b173d953ba52ce262f73ce3734b0e40e"
code = explorer.eth_getCode(addr)
print()
print(code)
