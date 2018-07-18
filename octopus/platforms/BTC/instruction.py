from octopus.core.instruction import Instruction

import struct


class BitcoinInstruction(Instruction):
    """BTC Instruction

    TODO

    """
    def __init__(self, opcode, name,
                 operand_size, pops, pushes, fee,
                 description, operand=None,
                 operand_interpretation=None,
                 offset=0, xref=None):
        """ TODO """
        super().__init__(opcode=opcode, name=name,
                         operand_size=operand_size, pops=pops, pushes=pushes,
                         fee=fee, description=description, operand=operand,
                         operand_interpretation=operand_interpretation,
                         offset=offset, xref=xref)

    # redefinition of this function
    def __str__(self):
        """ String representation of the instruction """
        output = ''
        if self.has_operand:
            if type(self.operand) == int:
                output = self.name + '' + self.operand.hex()
            else:
                if self.operand_size < 5:  # in ['', 'OP_PUSHDATA1', 'OP_PUSHDATA2']:
                    output = '%d' % int.from_bytes(self.operand,
                                                   byteorder='little', signed=True)
                elif self.name == '' or self.has_length_operand:
                    output = self.operand.hex()
                else:
                    output = self.name + ' ' + self.operand.hex()
        else:
            # format to be compliant with result from RPC call
            if (self.opcode >= 0x51 and self.opcode < 0x5A) or self.name == 'OP_0':
                output = self.name[-1]
            elif self.opcode >= 0x5A and self.opcode <= 0x60:
                output = self.name[-2:]
            else:
                output = self.name
        return output

    @property
    def has_length_operand(self):
        return self.name in ['OP_PUSHDATA1', 'OP_PUSHDATA2', 'OP_PUSHDATA4']

    def format_operand_size(self):
        if self.name == 'OP_PUSHDATA1':
            self.operand_size = struct.unpack('<B', self.operand_size)[0]
        elif self.name == 'OP_PUSHDATA2':
            self.operand_size = struct.unpack(b"<H", self.operand_size)[0]
        elif self.name == 'OP_PUSHDATA4':
            self.operand_size = struct.unpack(b"<I", self.operand_size)[0]
        else:
            pass

    def format_length_operand(self, value):
        if self.name == 'OP_PUSHDATA1':
            return value.to_bytes(1, 'little')
        elif self.name == 'OP_PUSHDATA2':
            return value.to_bytes(2, 'little')
        elif self.name == 'OP_PUSHDATA4':
            return value.to_bytes(4, 'little')
        else:
            pass

    # overwrite
    @property
    def bytes(self):
        """ Encoded instruction """
        byte = bytearray()
        byte.append(self.opcode)
        if self.has_length_operand:
            [byte.append(x) for x in self.format_length_operand(len(self.operand))]
        if self.operand:
            [byte.append(x) for x in self.operand]
        return "".join(map(chr, byte))

    # overwrite
    @property
    def size(self):
        """ Size of the encoded instruction """
        if self.has_length_operand:
            return self.operand_size + self.operand_size + 1
        else:
            return self.operand_size + 1
