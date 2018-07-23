from octopus.core.utils import bytecode_to_bytes


class BytecodeEmptyException(Exception):
    """Exception raised when bytecode is None"""
    pass


class Disassembler(object):
    """ Generic Disassembler class """

    def __init__(self, asm, bytecode=None):
        self.bytecode = bytecode
        self.instructions = list()
        self.reverse_instructions = dict()
        self.asm = asm

    def attributes_reset(self):
        """Reset instructions class attributes """
        self.instructions = list()
        self.reverse_instructions = dict()

    def disassemble_opcode(self, bytecode, offset=0):
        """ Generic method to disassemble one instruction """
        raise NotImplementedError

    def disassemble(self, bytecode=None, offset=0, r_format='list'):
        """Generic method to disassemble bytecode

        :param bytecode: bytecode sequence
        :param offset: start offset
        :param r_format: output format ('list'/'text'/'reverse')
        :type bytecode: bytes, str
        :type offset: int
        :type r_format: list, str, dict
        :return: dissassembly result depending of r_format
        :rtype: list, str, dict
        """
        # reinitialize class variable
        self.attributes_reset()

        self.bytecode = bytecode if bytecode else self.bytecode
        if not self.bytecode:
            raise BytecodeEmptyException()

        self.bytecode = bytecode_to_bytes(self.bytecode)

        while offset < len(self.bytecode):
            instr = self.disassemble_opcode(self.bytecode[offset:], offset)
            offset += instr.size
            self.instructions.append(instr)

        # fill reverse instructions
        self.reverse_instructions = {k: v for k, v in
                                     enumerate(self.instructions)}

        # return instructions
        if r_format == 'list':
            return self.instructions
        elif r_format == 'text':
            return '\n'.join(map(str, self.instructions))
        elif r_format == 'reverse':
            return self.reverse_instructions

    def disassemble_contract(self, contract):
        """ Generic method to disassemble a Contract """

        # reinitialize class variable
        self.attributes_reset()
        # update class bytecode
        self.bytecode = contract.bytecode

        self.disassemble(self.bytecode)
