#
# Title: CFG reconstruction of ETH smart contract (evm)
# Date: 06/29/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.analysis.graph import CFGGraph
from octopus.platforms.ETH.cfg import EthereumCFG

# ethernaut0 bytecode
file_name = "examples/ETH/evm_bytecode/Zeppelin_Hello_ethernaut0.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex)

# generic visualization api
graph = CFGGraph(cfg)
graph.view()
