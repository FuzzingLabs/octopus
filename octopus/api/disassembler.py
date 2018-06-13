import binascii


class Disassembler(object):

    def __init__(self, bytecode, asm):
        self.bytecode = bytecode
        self.instructions = list()
        self.reverse_instructions = dict()
        self.asm = asm

    def disassemble_opcode(self, bytecode, offset=0):
        '''
        TODO
        '''
        raise NotImplementedError

    def disassemble(self, bytecode=None, offset=0, r_format='list'):
        '''
        TODO
        '''
        self.bytecode = bytecode if bytecode else self.bytecode

        # convert hex to bytes
        if str(self.bytecode).startswith('0x'):
            self.bytecode = str(self.bytecode)[2:]
        if isinstance(self.bytecode, str):
            self.bytecode = binascii.unhexlify(self.bytecode)

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
        '''
        TODO
        '''
        self.instructions = list()
        self.reverse_instructions = dict()

        self.bytecode = contract.bytecode
        self.disassemble(self.bytecode)
