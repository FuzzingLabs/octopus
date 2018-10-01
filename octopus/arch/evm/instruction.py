from octopus.core.instruction import Instruction


class EvmInstruction(Instruction):
    """ETH Instruction

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
                         offset=offset, xref=xref)

    @property
    def group(self):
        '''Instruction classification as per the yellow paper'''
        classes = {0: 'Stop and Arithmetic Operations',
                   1: 'Comparison & Bitwise Logic Operations',
                   2: 'SHA3',
                   3: 'Environmental Information',
                   4: 'Block Information',
                   5: 'Stack, Memory, Storage and Flow Operations',
                   6: 'Push Operations',
                   7: 'Push Operations',
                   8: 'Duplication Operations',
                   9: 'Exchange Operations',
                   0xa: 'Logging Operations',
                   0xf: 'System operations'}
        return classes.get(self.opcode >> 4, 'Invalid instruction')

    @property
    def is_terminator(self):
        """ True if the instruction is a basic block terminator """
        return self.is_branch or self.is_halt

    @property
    def is_branch_conditional(self):
        """ Return list if the instruction is a jump """
        return self.semantics in ['JUMPI']

    @property
    def is_branch_unconditional(self):
        """ Return list if the instruction is a jump """
        return self.semantics in ['JUMP']

    @property
    def is_system(self):
        """ True if the instruction is a system operation """
        return self.group == 'System operations'

    @property
    def is_arithmetic(self):
        """ True if the instruction is an arithmetic operation """
        return self.group == 'Stop and Arithmetic Operations'

    @property
    def is_comparaison_logic(self):
        """ True if the instruction is a Comparison & Bitwise Logic Operations """
        return self.group == 'Comparison & Bitwise Logic Operations'

    @property
    def is_sha3(self):
        """ True if the instruction is SHA3"""
        return self.group == 'SHA3'

    @property
    def is_environmental(self):
        """ True if the instruction access enviromental data """
        return self.group == 'Environmental Information'

    @property
    def uses_block_info(self):
        """ True if the instruction access block information """
        return self.group == 'Block Information'

    @property
    def uses_stack_block_storage_info(self):
        """ True if the instruction are in the group Stack, Memory, Storage and Flow Operations """
        return self.group == 'Stack, Memory, Storage and Flow Operations'

    @property
    def is_push(self):
        """ True if the instruction is a push Operations """
        return self.group == 'Push Operations'

    @property
    def have_xref(self):
        """ True if the instruction is a basic block terminator """
        return self.is_branch

    def set_xref(self, v):
        """ TODO """
        self._xref = int.from_bytes(v, byteorder='big')

    @property
    def is_call(self):
        """ Return list if the instruction is a basic block terminator """
        return self.semantics in ('CALL', 'CALLCODE',
                                  'DELEGATECALL', 'STATICCALL')

    @property
    def is_halt(self):
        """ Return list if the instruction is a basic block terminator """
        return self.semantics in ('RETURN', 'STOP', 'INVALID',
                                  'SELFDESTRUCT', 'REVERT')
