from octopus.core.instruction import Instruction


class NeoInstruction(Instruction):
    """NEO Instruction

    TODO

    """
    def __init__(self, opcode, name,
                 operand_size, pops, pushes, fee,
                 description, operand=None,
                 operand_interpretation=None, offset=0, xref=None):
        """ TODO """
        super().__init__(opcode=opcode, name=name,
                         operand_size=operand_size, pops=pops, pushes=pushes,
                         fee=fee, description=description, operand=operand,
                         operand_interpretation=operand_interpretation,
                         offset=offset)

    @property
    def has_length_operand(self):
        """ True if the instruction uses an immediate operand to define the lenght of operand """
        return self.name in ['SYSCALL']

    # overwrite this function to take care of has_length_operand
    @property
    def size(self):
        """ Size of the encoded instruction """
        if self.has_length_operand:
            # add size of lengh operand
            return self.operand_size + 2
        return self.operand_size + 1

    @property
    def group(self):
        """ Instruction classification per group """
        classes = {0x00: 'Constant',
                   0x61: 'Flow control',
                   0x6A: 'Stack',
                   0x7E: 'Splice',
                   0x83: 'Bitwise logic',
                   0x8B: 'Arithmetic',
                   0xA6: 'Crypto',
                   0xC0: 'Array',
                   0xF0: 'Exceptions'}

        last_class = classes.get(0)
        for k, v in classes.items():
            if self.opcode >= k:
                last_class = v
            else:
                return last_class
        return last_class

    @property
    def is_constant(self):
        return self.group == 'Constant'

    @property
    def is_flow_control(self):
        return self.group == 'Flow control'

    @property
    def is_stack(self):
        return self.group == 'Stack'

    @property
    def is_splice(self):
        return self.group == 'Splice'

    @property
    def is_bitwise_logic(self):
        return self.group == 'Bitwise logic'

    @property
    def is_arithmetic(self):
        return self.group == 'Arithmetic'

    @property
    def is_crypto(self):
        return self.group == 'Crypto'

    @property
    def is_array(self):
        return self.group == 'Array'

    @property
    def is_exceptions(self):
        return self.group == 'Exceptions'

    @property
    def is_branch_conditional(self):
        """ Return list if the instruction is a jump """
        return self.name in ['JMPIF', 'JMPIFNOT']

    @property
    def is_branch_unconditional(self):
        """ Return list if the instruction is a jump """
        return self.name in ['JMP']

    @property
    def is_branch(self):
        """ True if the instruction is a jump """
        return self.is_branch_conditional or self.is_branch_unconditional

    @property
    def is_halt(self):
        """ Return list if the instruction is a basic block terminator """
        return (self.name in ['RET'] or self.is_exceptions)

    @property
    def is_terminator(self):
        """ True if the instruction is a basic block terminator """
        return self.is_branch or self.is_halt

    @property
    def have_xref(self):
        """ True if the instruction operand is a reference to an other instruction """
        return self.is_branch or (self.name in ['CALL'])
