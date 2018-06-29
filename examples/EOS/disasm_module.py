#
# Title: Disassemble EOS smart contract (.wasm)
# Date: 06/29/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.platforms.EOS.disassembler import EosDisassembler

# complete wasm module
file_name = "examples/EOS/samples/eos_ping.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# just disassembly
disasm = EosDisassembler()

# because we provide full module bytecode
# we need to use disassemble_module()
# otherwise just disassemble() is enough
text = disasm.disassemble_module(raw, r_format="text")
print(text)
