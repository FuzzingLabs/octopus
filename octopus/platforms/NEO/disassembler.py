import io

from octopus.engine.disassembler import Disassembler

from octopus.platforms.NEO.instruction import NeoInstruction
from octopus.platforms.NEO.avm import Avm


class NeoDisassembler(Disassembler):

    def __init__(self, bytecode=None):
        Disassembler.__init__(self, bytecode=bytecode, asm=Avm())

    def disassemble_opcode(self, bytecode, offset=0):
        '''
        TODO
        '''

        wallet = io.BytesIO(bytecode)
        opcode = int.from_bytes(wallet.read(1), byteorder='big')

        invalid = ('INVALID', 0, 0, 0, 0, 'Unknown opcode')
        name, operand_size, pops, pushes, gas, description = \
            self.asm.table.get(opcode, invalid)
        instruction = NeoInstruction(opcode, name, operand_size, pops, pushes,
                                     gas, description, offset=offset)
        if instruction.has_length_operand:
            instruction.operand_size = int.from_bytes(wallet.read(1), byteorder='big')
        if instruction.has_operand:
            instruction.operand = wallet.read(instruction.operand_size)
        return instruction

    def disassemble(self, bytecode=None, offset=0, r_format='list'):
        '''
        TODO
        '''
        self.bytecode = str(bytecode) if bytecode else str(self.bytecode)

        self.instructions = list()
        self.reverse_instructions = dict()

        return super().disassemble(bytecode, offset, r_format)
