from octopus.arch.wasm.cfg import WasmCFG


# Eos smart contract == wasm module
class EosCFG(WasmCFG):
    def __init__(self, module_bytecode):
        WasmCFG.__init__(self,
                         module_bytecode=module_bytecode)
