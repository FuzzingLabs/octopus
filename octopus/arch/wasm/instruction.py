from octopus.core.instruction import Instruction

from wasm.opcodes import (INSN_ENTER_BLOCK,
                          INSN_LEAVE_BLOCK,
                          INSN_NO_FLOW)  # INSN_BRANCH

from octopus.arch.wasm.wasm import _groups


class WasmInstruction(Instruction):
    """Wasm Instruction

    TODO

    """
    def __init__(self, opcode, name, imm_struct, operand_size, flags, insn_byte,
                 pops, pushes, description, operand_interpretation=None, offset=0):
        """ TODO """
        self.opcode = opcode
        self.offset = offset
        self.name = name
        self.description = description
        self.operand_size = operand_size
        self.flags = flags
        self.operand = insn_byte  # Immediate operand if any
        # specific interpretation of operand value
        self.operand_interpretation = operand_interpretation
        self.insn_byte = insn_byte
        self.pops = pops
        self.pushes = pushes
        self.imm_struct = imm_struct
        self.xref = list()
        self.ssa = None

    def __eq__(self, other):
        """ Instructions are equal if all features match  """
        return self.opcode == other.opcode and\
            self.name == other.name and\
            self.insn_byte == other.insn_byte and\
            self.operand_size == other.operand_size and\
            self.pops == other.pops and\
            self.pushes == other.pushes and\
            self.operand_interpretation == other.operand_interpretation and\
            self.description == other.description

    def __str__(self):
        """ String representation of the instruction """
        if self.operand_interpretation:
            return self.operand_interpretation
        # elif self.operand:
        #    return self.name + str(self.operand)
        else:
            return self.name

    @property
    def group(self):
        """ Instruction classification per group """
        last_class = _groups.get(0)
        for k, v in _groups.items():
            if self.opcode >= k:
                last_class = v
            else:
                return last_class
        return last_class

    @property
    def is_branch_conditional(self):
        """ Return True if the instruction is a conditional jump """
        return self.name in ['br_if', 'br_table', 'if']

    @property
    def is_branch_unconditional(self):
        """ Return True if the instruction is a unconditional jump """
        return self.name in ['br']

    @property
    def is_call(self):
        """ True if the instruction is a call instruction """
        return self.name in ['call', 'call_indirect']

    @property
    def is_branch(self):
        return self.is_branch_conditional or self.is_branch_unconditional

    @property
    def is_halt(self):
        """ Return True if the instruction is a branch terminator """
        return self.flags & INSN_NO_FLOW
        # return self.name in ['return']  # unreachable

    @property
    def is_terminator(self):
        """ True if the instruction is a basic block terminator """
        return self.is_branch or self.is_halt

    @property
    def is_block_starter(self):
        """ Return True if the instruction is a basic block starter """
        return self.flags & INSN_ENTER_BLOCK

    @property
    def is_block_terminator(self):
        """ Return True if the instruction is a basic block terminator """
        return self.flags & INSN_LEAVE_BLOCK
