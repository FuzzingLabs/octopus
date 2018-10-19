from octopus.engine.helper import helper as hlp
from z3 import UDiv, ULT, UGT

from logging import getLogger
logging = getLogger(__name__)

# =======================================
# #            SSA Simplifier           #
# =======================================


class EvmSSASimplifier(object):
    def __init__(self):
        self._dispatch_function = {
            # arithmetic
            'ADD': self.symbolic_add,
            'SUB': self.operate_SUB,
            'MUL': self.operate_MUL,
            'DIV': self.operate_DIV,
            'MOD': self.operate_MOD,
            'SDIV': self.operate_SDIV,
            'SMOD': self.operate_SMOD,
            'ADDMOD': self.operate_ADDMOD,
            'MULMOD': self.operate_MULMOD,
            'EXP': self.operate_EXP,
            # SIGNEXTEND
            # logic
            'LT': self.operate_LT,
            'GT': self.operate_GT,
            'SLT': self.operate_SLT,
            'SGT': self.operate_SGT,
            'EQ': self.operate_EQ,
            'ISZERO': self.operate_ISZERO,
            'AND': self.operate_AND,
            'OR': self.operate_OR,
            'XOR': self.operate_XOR,
            # 'NOT': self.operate_NOT,
            # 'BYTE': self.operate_BYTE,
        }

    def is_all_constant(self, list):
        if [True] * len(list) == [i.ssa.is_constant for i in list]:
            return True
        return False

    def resolve_instr_ssa(self, instr):
        # SSA_TYPE_CONSTANT
        if instr.ssa.is_constant and instr.operand_interpretation:
            return instr.operand_interpretation
        # SSA_TYPE_FUNCTION
        elif instr.ssa.is_function:
            # args are all constants (most commun case)
            if self.is_all_constant(instr.ssa.args):
                values = [i.operand_interpretation for i in instr.ssa.args]
                result = self.symbolic_dispatcher(instr.name, values)
                # logging.warning('.. %x', result)
                return result
            else:
                # TODO: recursive resolve_instr_ir
                logging.warning('args not all constant')
                return None

        else:
            raise Exception('SSA_TYPE Unknown')
        return None

    def symbolic_dispatcher(self, mnemonic, values):

        fn = self._dispatch_function.get(mnemonic, None)
        return fn(*values)

    # arithmetics
    def symbolic_add(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 + s1)

    def operate_SUB(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 - s1)

    def operate_MUL(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 * s1)

    def operate_DIV(self, *values):
        if values[1] == 0:
            return 0
        else:
            return hlp.get_concrete_int(UDiv(values[0] / values[1]))

    def operate_MOD(self, *values):
        return hlp.get_concrete_int(0 if values[1] == 0 else values[0] % values[1])

    def operate_SDIV(self, *values):
        s0, s1 = values[0], values[1]
        sign = -1 if (s0 / s1) < 0 else 1
        computed = sign * (abs(s0) / abs(s1))
        return hlp.get_concrete_int(computed)

    def operate_SMOD(self, *values):
        sign = -1 if values[0] < 0 else 1
        computed = sign * (abs(values[0]) % abs(values[1]))
        return hlp.get_concrete_int(computed)

    def operate_ADDMOD(self, *values):
        s0, s1, s2 = values[0], values[1], values[2]
        return hlp.get_concrete_int((s0 + s1) % s2 if s2 else 0)

    def operate_MULMOD(self, *values):
        s0, s1, s2 = values[0], values[1], values[2]
        return hlp.get_concrete_int((s0 * s1) % s2 if s2 else 0)

    def operate_EXP(self, *values):
        base, exponent = values[0], values[1]
        return hlp.get_concrete_int(pow(base, exponent))

        # logic
    def operate_LT(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(ULT(s0, s1))

    def operate_GT(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(UGT(s0, s1))

    def operate_SLT(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 < s1)

    def operate_SGT(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 > s1)

    def operate_EQ(self, *values):
        return hlp.get_concrete_int(values[0] == values[1])

    def operate_ISZERO(self, *values):
        return hlp.get_concrete_int(values[0] == 0)

    def operate_AND(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 & s1)

    def operate_OR(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 | s1)

    def operate_XOR(self, *values):
        s0 = hlp.convert_to_bitvec(values[0])
        s1 = hlp.convert_to_bitvec(values[1])
        return hlp.get_concrete_int(s0 ^ s1)

    # def operate_NOT(self, *values):
    #    return hlp.get_concrete_int(values[0] & values[1])

    # def operate_BYTE(self, *values):
    #    return
