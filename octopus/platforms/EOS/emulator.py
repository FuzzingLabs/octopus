from octopus.arch.wasm.emulator import WasmSSAEmulatorEngine


# Eos smart contract == wasm module
class EosSSAEmulatorEngine(WasmSSAEmulatorEngine):
    def __init__(self, bytecode=None):
        WasmSSAEmulatorEngine.__init__(self,
                                       bytecode=bytecode)
