from octopus.arch.wasm.analyzer import WasmModuleAnalyzer


# Eos smart contract == wasm module
class EosAnalyzer(WasmModuleAnalyzer):
    def __init__(self, module_bytecode, analysis=True):
        WasmModuleAnalyzer.__init__(self,
                                    module_bytecode=module_bytecode,
                                    analysis=analysis)
