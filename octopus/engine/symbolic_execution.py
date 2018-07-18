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
