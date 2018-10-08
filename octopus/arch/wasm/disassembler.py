from octopus.engine.disassembler import Disassembler
from octopus.core.function import Function
from octopus.core.utils import bytecode_to_bytes

from octopus.arch.wasm.instruction import WasmInstruction
from octopus.arch.wasm.wasm import Wasm

from octopus.arch.wasm.decode import decode_module
# from wasm.decode import decode_module
from wasm.modtypes import CodeSection
from wasm.compat import byte2int
from wasm.opcodes import OPCODE_MAP
from wasm.formatter import format_instruction

from collections import namedtuple
inst_namedtuple = namedtuple('Instruction', 'op imm len')


class WasmDisassembler(Disassembler):

    def __init__(self, bytecode=None):
        Disassembler.__init__(self, asm=Wasm(), bytecode=bytecode)

    def disassemble_opcode(self, bytecode=None, offset=0):
        '''
        based on decode_bytecode()
        https://github.com/athre0z/wasm/blob/master/wasm/decode.py

        '''

        bytecode_wnd = memoryview(bytecode)
        opcode_id = byte2int(bytecode_wnd[0])

        # default value
        # opcode:(mnemonic/name, imm_struct, pops, pushes, description)
        invalid = ('INVALID', 0, 0, 0, 'Unknown opcode')
        name, imm_struct, pops, pushes, description = \
            self.asm.table.get(opcode_id, invalid)

        operand_size = 0
        operand = None
        operand_interpretation = None

        if imm_struct is not None:
            operand_size, operand, _ = imm_struct.from_raw(None, bytecode_wnd[1:])
            insn = inst_namedtuple(OPCODE_MAP[opcode_id], operand, 1 + operand_size)
            operand_interpretation = format_instruction(insn)
        insn_byte = bytecode_wnd[:1 + operand_size].tobytes()
        instruction = WasmInstruction(opcode_id, name, imm_struct, operand_size,
                                      insn_byte, pops, pushes, description,
                                      operand_interpretation=operand_interpretation,
                                      offset=offset)
        # print('%d %s' % (offset, str(instruction)))
        return instruction

    def disassemble(self, bytecode=None, offset=0, r_format='list'):
        """Disassemble WASM bytecode

        :param bytecode: bytecode sequence
        :param offset: start offset
        :param r_format: output format ('list'/'text'/'reverse')
        :type bytecode: bytes, str
        :type offset: int
        :type r_format: list, str, dict
        :return: dissassembly result depending of r_format
        :rtype: list, str, dict

        :Example:

        >>> disasm = WasmDisassembler()
        >>>
        >>> disasm.disassemble(r_format='text')
        >>> 'block -1\ni32.const 24\ncall 28\ni32.const 0\nreturn\nend'
        >>>
        >>> disasm.disassemble(r_format='text')
        >>> [<octopus.arch.wasm.instruction.WasmInstruction at 0x7f80243120b8>,
             ...
             <octopus.arch.wasm.instruction.WasmInstruction at 0x7f8024312588>,
             <octopus.arch.wasm.instruction.WasmInstruction at 0x7f80243121d0>]
        >>>
        >>> disasm.disassemble(r_format='reverse')
        >>> {0: <octopus.arch.wasm.instruction.WasmInstruction at 0x7f8024319d68>,
             ...
             4: <octopus.arch.wasm.instruction.WasmInstruction at 0x7f802431fa58>,
             5: <octopus.arch.wasm.instruction.WasmInstruction at 0x7f802431fc18>}
        """

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

        bytecode = bytecode_to_bytes(module_bytecode)

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
