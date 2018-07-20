#
# Title: Call graph EOS smart contract (.wasm)
# Date: 07/04/18
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

# visualize
cfg.visualize_call_flow()
