#
# Title: Retreive smart contract code using InfuraExplorer
# Date: 06/29/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.platforms.ETH.explorer import EthereumInfuraExplorer
from octopus.platforms.ETH.explorer import INFURA_ROPSTEN
from octopus.platforms.ETH.contract import EthereumContract

# connection to ROPSTEN network (testnet)
explorer = EthereumInfuraExplorer("bHuaQhX91nkQBac8Wtgj",
                                  network=INFURA_ROPSTEN)
# connection to MAINNET network (mainnet)
# explorer = EthereumInfuraExplorer("bHuaQhX91nkQBac8Wtgj")

# test infura access
block_number = explorer.eth_blockNumber()
print('blockNumber = %d' % block_number)

# retrieve code of this smart contract
addr = "0x3c6B10a5239B1a8A27398583F49771485382818F"
code = explorer.eth_getCode(addr)
print('code = %s' % code)

# equivalent using contract class
# get_online_bytecode used eth_getCode
contract = EthereumContract(address=addr)
contract.get_online_bytecode(explorer)
code2 = contract.bytecode
print('code2 = %s' % code2)

# same value?
print()
print('code == code2: %s' % (str(code) == str(code2)))
