from octopus.arch.wasm.disassembler import WasmDisassembler


# Eos smart contract == wasm module
class EosDisassembler(WasmDisassembler):
    def __init__(self, bytecode=None, asm=None):
        WasmDisassembler.__init__(self,
                                  bytecode=bytecode,
                                  asm=asm)
