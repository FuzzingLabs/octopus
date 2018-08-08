#
# Title: Visualization of instructions count
#        per function and group of EOS smart contract
#
# Date: 08/08/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.platforms.EOS.cfg import EosCFG

# complete wasm module
file_name = "examples/EOS/samples/eos_ping.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = EosCFG(raw)

# visualization
cfg.visualize_instrs_per_funcs()
