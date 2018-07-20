#
# Title: Call & CFG graph for fibonacci wasm module
# Date: 07/16/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.arch.wasm.cfg import WasmCFG
from octopus.analysis.graph import CFGGraph

# complete wasm module
file_name = "examples/wasm/samples/fib.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = WasmCFG(raw)

# visualize CFGGraph
graph = CFGGraph(cfg)
graph.view_functions()

# visualize CallGraph
cfg.visualize_call_flow()
