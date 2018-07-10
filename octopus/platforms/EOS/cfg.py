from octopus.arch.wasm.cfg import WasmCFG


# Eos smart contract == wasm module
class EosCFG(WasmCFG):
    def __init__(self, module_bytecode, static_analysis=True):
        WasmCFG.__init__(self,
                         module_bytecode=module_bytecode,
                         static_analysis=static_analysis)
