from octopus.platforms.NEO.disassembler import NeoDisassembler

# lock contract
file_name = "examples/NEO/samples/Lock.bytecode"

# read file
with open(file_name) as f:
    bytecode = f.read()

disasm = NeoDisassembler()

print(disasm.disassemble(bytecode, r_format='text'))
# PUSH6
# NEWARRAY
# TOALTSTACK
# FROMALTSTACK
# DUP
# TOALTSTACK
# PUSH0
# PUSH2
# ROLL
# SETITEM
# FROMALTSTACK
# ....
# PICKITEM
# NOP
# FROMALTSTACK
# DROP
# RET
