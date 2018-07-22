from octopus.platforms.BTC.disassembler import BitcoinDisassembler

# Witness Script
file_name = "examples/BTC/witness_script.hex"

# read file
with open(file_name) as f:
    bytecode = f.read()

disasm = BitcoinDisassembler()

print(disasm.disassemble(bytecode, r_format='text'))