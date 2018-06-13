from octopus.api.disassembler import Disassembler

from .instruction import EosInstruction
from .wasm import Wasm

from wasm.decode import decode_module
from wasm.compat import byte2int
from wasm.opcodes import OPCODE_MAP
from wasm.formatter import format_instruction


from collections import namedtuple
inst_namedtuple = namedtuple('Instruction', 'op imm len')


class EosDisassembler(Disassembler):

    def __init__(self, bytecode=None, instructions=None):
        Disassembler.__init__(self, bytecode=bytecode, asm=Wasm())

    def disassemble_opcode(self, bytecode=None, offset=0):
        '''
        based on decode_bytecode()
        https://github.com/athre0z/wasm/blob/master/wasm/decode.py

        '''

        bytecode_wnd = memoryview(bytecode)
        opcode_id = byte2int(bytecode_wnd[0])

        # default value
        # opcode:(mnemonic/name, imm_struct, flags, pops, pushes, description)
        invalid = ('INVALID', 0, 0, 0, 0, 0, 'Unknown opcode')
        name, imm_struct, flags, pops, pushes, description = \
            self.asm.table.get(opcode_id, invalid)

        operand_size = 0
        operand = None
        operand_interpretation = None

        if imm_struct is not None:
            operand_size, operand, _ = imm_struct.from_raw(None, bytecode_wnd[1:])
            insn = inst_namedtuple(OPCODE_MAP[opcode_id], operand, 1 + operand_size)
            operand_interpretation = format_instruction(insn)
        insn_byte = bytecode_wnd[:1 + operand_size].tobytes()
        instruction = EosInstruction(opcode_id, name, imm_struct, operand_size, flags,
                                     insn_byte, pops, pushes, description,
                                     operand_interpretation=operand_interpretation,
                                     offset=offset)
        #print('%d %s' % (offset, str(instruction)))
        return instruction

    def disassemble(self, bytecode=None, offset=0, r_format='list'):

        self.instructions = list()
        self.reverse_instructions = dict()

        return super().disassemble(bytecode, offset, r_format)

    def disassemble_module(self, bytecode=None, offset=0, r_format='list'):
        return self.disassemble(bytecode, offset, r_format)
