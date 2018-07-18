from octopus.engine.emulator import EmulatorEngine

# =======================================
# #         WASM Emulator               #
# =======================================


class WasmEmulatorEngine(EmulatorEngine):

    def __init__(self, instructions):
        """ TODO """
        raise NotImplementedError

    def emulate(self, state, depth=0):
        """ TODO """
        raise NotImplementedError

    def emulate_function(self):
        """ TODO """
        raise NotImplementedError

    def emulate_one_instruction(self, instr, state, depth):
        """ TODO """
        raise NotImplementedError
