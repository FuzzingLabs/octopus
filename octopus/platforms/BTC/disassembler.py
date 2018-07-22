import io

from octopus.engine.disassembler import Disassembler

from octopus.platforms.BTC.instruction import BitcoinInstruction
from octopus.platforms.BTC.btcscript import BTCScript

# tested with http://chainquery.com/bitcoin-api/decodescript


class BitcoinDisassembler(Disassembler):

    def __init__(self, bytecode=None):
        Disassembler.__init__(self, bytecode=bytecode, asm=BTCScript())

    def disassemble_opcode(self, bytecode, offset=0):
        '''
        TODO
        '''
        wallet = io.BytesIO(bytecode)
        opcode = int.from_bytes(wallet.read(1), byteorder='big')

        invalid = ('OP_INVALIDOPCODE', 0, 0, 0, 0, 'Matches any opcode that is not yet assigned.')
        name, operand_size, pops, pushes, gas, description = \
            self.asm.table.get(opcode, invalid)
        instruction = BitcoinInstruction(opcode, name, operand_size, pops, pushes,
                                         gas, description, offset=offset)
        if instruction.has_length_operand:
            instruction.operand_size = wallet.read(instruction.operand_size)
            instruction.format_operand_size()
        if instruction.has_operand:
            instruction.operand = wallet.read(instruction.operand_size)
        return instruction

    def disassemble(self, bytecode=None, offset=0, r_format='list'):
        '''
        TODO
        '''

        #self.bytecode = str(bytecode) if bytecode else str(self.bytecode)
        self.instructions = list()
        self.reverse_instructions = dict()

        return super().disassemble(bytecode, offset, r_format)
