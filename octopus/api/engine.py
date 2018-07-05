class VMstate(object):

    def __init__(self, gas=1000000):
        """ TODO """
        raise NotImplementedError

    def details(self):
        """ TODO """
        raise NotImplementedError


# =======================================
# #     Symbolic Execution Engine       #
# =======================================

class SymbolicExecutionEngine(object):

    def __init__(self, bytecode=None, instructions=None, contract=None, modules=None, dynamic_loader=None, max_depth=10):
        """ TODO """
        raise NotImplementedError

    def sym_exec_contract(self, contract):
        """ TODO """
        raise NotImplementedError

    def sym_exec_single_instr(self, instr, context, state, depth, constraints):
        """ TODO """
        raise NotImplementedError


# =======================================
# #         SSA Engine                  #
# =======================================

class SSAEngine(object):

    def __init__(self, instructions):
        """ TODO """
        raise NotImplementedError

    def emulate(self, state, depth=0):
        """ TODO """
        raise NotImplementedError

    def emulate_one_instruction(self, instr, state, depth):
        """ TODO """
        raise NotImplementedError
