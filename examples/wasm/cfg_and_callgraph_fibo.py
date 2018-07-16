#
# Title: Call & CFG graph for fibonacci wasm module
# Date: 07/16/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.platforms.EOS.cfg import EosCFG
from octopus.api.graph import CallGraph, CFGGraph

# complete wasm module
file_name = "examples/wasm/samples/fib.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = EosCFG(raw)
# retrieve nodes and edges
nodes, edges = cfg.get_functions_call_edges()

# visualize CFGGraph
graph = CFGGraph(cfg)
graph.view_functions()

# visualize CallGraph
graph = CallGraph(nodes, edges)
graph.view()

# visualize module content
analyzer = cfg.analyzer
print(analyzer.show())
