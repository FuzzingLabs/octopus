from octopus.arch.wasm.cfg import WasmCFG


# Eos smart contract == wasm module
class EosCFG(WasmCFG):
    def __init__(self, module_bytecode):
        WasmCFG.__init__(self,
                         module_bytecode=module_bytecode)

    def visualize_instrs_per_funcs(self, show=True, save=True,
                                   out_filename="eos_func_analytic.png",
                                   fontsize=8):
        super().visualize_instrs_per_funcs(show, save, out_filename, fontsize)
