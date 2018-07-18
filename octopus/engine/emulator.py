# =======================================
# #         Emulator                    #
# =======================================


class EmulatorEngine(object):

    def __init__(self, instructions):
        """ TODO """
        raise NotImplementedError

    def emulate(self, state, depth=0):
        """ TODO """
        raise NotImplementedError

    def emulate_one_instruction(self, instr, state, depth):
        """ TODO """
        raise NotImplementedError