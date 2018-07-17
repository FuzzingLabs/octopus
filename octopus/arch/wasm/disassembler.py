from octopus.api.disassembler import Disassembler
from octopus.api.function import Function

from .instruction import WasmInstruction
from .wasm import Wasm

from wasm.decode import decode_module
from wasm.modtypes import CodeSection
from wasm.compat import byte2int
from wasm.opcodes import OPCODE_MAP
from wasm.formatter import format_instruction

import binascii
from collections import namedtuple
inst_namedtuple = namedtuple('Instruction', 'op imm len')


class WasmDisassembler(Disassembler):

    def __init__(self, bytecode=None, asm=None):
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
        instruction = WasmInstruction(opcode_id, name, imm_struct, operand_size, flags,
                                      insn_byte, pops, pushes, description,
                                      operand_interpretation=operand_interpretation,
                                      offset=offset)
        # print('%d %s' % (offset, str(instruction)))
        return instruction

    def disassemble(self, bytecode=None, offset=0, r_format='list'):

        self.instructions = list()
        self.reverse_instructions = dict()

        return super().disassemble(bytecode, offset, r_format)

    def extract_functions_code(self, module_bytecode):
        functions = list()
        mod_iter = iter(decode_module(module_bytecode))
        _, _ = next(mod_iter)
        sections = list(mod_iter)

        # iterate over all section
        #code_data = [cur_sec_data for cur_sec, cur_sec_data in sections if isinstance(cur_sec_data.get_decoder_meta()['types']['payload'], CodeSection)][0]
        for cur_sec, cur_sec_data in sections:
            sec = cur_sec_data.get_decoder_meta()['types']['payload']
            if isinstance(sec, CodeSection):
                code_data = cur_sec_data
                break
        if not code_data:
            raise ValueError('No functions/codes in the module')
        for idx, func in enumerate(code_data.payload.bodies):
            instructions = self.disassemble(func.code.tobytes())
            cur_function = Function(0, instructions[0])
            cur_function.instructions = instructions

            functions.append(cur_function)
        return functions

    def disassemble_module(self, module_bytecode=None, offset=0, r_format='list'):

        if isinstance(module_bytecode, str):
            bytecode = binascii.unhexlify(module_bytecode)
        else:
            bytecode = module_bytecode

        functions = self.extract_functions_code(bytecode[offset:])
        self.instructions = [f.instructions for f in functions]

        # return instructions
        if r_format == 'list':
            return self.instructions
        elif r_format == 'text':
            text = ''
            for index, func in enumerate(functions):
                text += ('func %d\n' % index)
                text += ('\n'.join(map(str, func.instructions)))
                text += ('\n\n')
            return text
