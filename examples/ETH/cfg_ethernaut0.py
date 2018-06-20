
from octopus.api.graph import CFGGraph
from octopus.platforms.ETH.cfg import EthereumCFG

# lock contract
file_name = "bytecode/Zeppelin_Hello_ethernaut0.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex)

# generic visualization api
graph = CFGGraph(cfg)
graph.view_function()
