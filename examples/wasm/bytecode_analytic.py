#
# Title: Visualization of instructions count 
#        per function and group
#
# Date: 08/08/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.arch.wasm.cfg import WasmCFG

# complete wasm module
file_name = "examples/wasm/samples/hello_wasm_studio.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = WasmCFG(raw)

# visualization
cfg.visualize_instrs_per_funcs()
