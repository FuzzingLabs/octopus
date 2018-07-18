class Instruction(object):
    """Instruction """
    def __init__(self, opcode, name,
                 operand_size, pops, pushes, fee,
                 description, operand=None,
                 operand_interpretation=None, offset=0, xref=None):

        self.opcode = opcode
        self.offset = offset
        self.name = name
        self.description = description
        self.operand_size = operand_size
        self.operand = operand  # Immediate operand if any
        # specific interpretation of operand value
        # ex: operand value for JUMP = xref
        self.operand_interpretation = operand_interpretation
        self.pops = pops
        self.pushes = pushes
        self.fee = fee
        self.xref = xref
        self.ssa = None

    def __eq__(self, other):
        """ Instructions are equal if all features match  """
        return self.opcode == other.opcode and\
            self.name == other.name and\
            self.operand == other.operand and\
            self.operand_size == other.operand_size and\
            self.pops == other.pops and\
            self.pushes == other.pushes and\
            self.fee == other.fee and\
            self.offset == other.offset and\
            self.description == other.description

    def __simple_output_format(self, offset=True):
        output = self.name
        if self.has_operand:
            output += ' 0x%x' % int.from_bytes(self.operand,
                                               byteorder='big')

        if offset:
            return "%d %s" % (self._offset, output)
        else:
            return "%s" % output

    #def __repr__(self):
    #    """ Entire representation of the instruction
    #    output = 'Instruction(0x%x, %r, %d, %d, %d, %d, %r, %r, %r)' \
    #        % (self._opcode, self._name, self._operand_size,
    #            self._pops, self._pushes, self._fee,
    #            self._description, self._operand, self._offset)"""
    #    return self.__simple_output_format()

    def __str__(self):
        """ String representation of the instruction """
        return self.__simple_output_format(offset=False)

    @property
    def bytes(self):
        """ Encoded instruction """
        byte = bytearray()
        byte.append(self.opcode)
        if self.operand:
            [byte.append(x) for x in self.operand]
        return "".join(map(chr, byte))

    @property
    def offset_end(self):
        """ Location in the program (optional) """
        return self.offset + self.size - 1

    @property
    def semantics(self):
        """ Canonical semantics """
        return self.name

    @property
    def size(self):
        """ Size of the encoded instruction """
        return self.operand_size + 1

    @property
    def has_operand(self):
        """ True if the instruction uses an immediate operand """
        return self.operand_size > 0

    @property
    def is_branch_conditional(self):
        """ Return list if the instruction is a jump """
        raise NotImplementedError

    @property
    def is_branch_unconditional(self):
        """ Return list if the instruction is a jump """
        raise NotImplementedError

    @property
    def is_branch(self):
        """ True if the instruction is a jump """
        return self.is_branch_conditional or self.is_branch_unconditional

    @property
    def is_halt(self):
        """ Return list if the instruction is a basic block terminator """
        raise NotImplementedError

    @property
    def is_terminator(self):
        """ True if the instruction is a basic block terminator """
        raise NotImplementedError

    @property
    def have_xref(self):
        """ TODO """
        raise NotImplementedError
