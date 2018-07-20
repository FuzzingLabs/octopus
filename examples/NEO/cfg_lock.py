#
# Title: CFG reconstruction of Neo smart contract (.avm)
# Date: 06/13/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.analysis.graph import CFGGraph
from octopus.platforms.NEO.cfg import NeoCFG


# lock contract
file_name = "examples/NEO/samples/Lock.bytecode"

# read file
with open(file_name) as f:
    raw = f.read()

# create neo cfg - automatic static analysis
cfg = NeoCFG(raw)

# graph visualization
graph = CFGGraph(cfg, filename="Lock_cfg")
graph.view_functions()
