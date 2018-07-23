import io
import logging
import re

from octopus.engine.disassembler import Disassembler

from octopus.arch.evm.instruction import EvmInstruction
from octopus.arch.evm.evm import EVM


def runtime_code_detector(bytecode_hex):
    '''Check for presence of runtime code
    '''
    result = list(re.finditer('60.{2}604052', bytecode_hex))
    if len(result) > 1:
        position = result[1].start()
        logging.info("[+] Runtime code detected")
        return bytecode_hex[position:]
    return bytecode_hex


def swarm_hash_detector(bytecode_hex):
    '''Check for presence of Swarm hash at the end of bytecode
        https://github.com/ethereum/wiki/wiki/Swarm-Hash
    '''
    swarm_hash = bytecode_hex[-86:]
    # bzzr == 0x627a7a72
    if '627a7a72' in swarm_hash:
        logging.info("[+] Swarm hash detected in bytecodes")
        bytecode_hex = bytecode_hex[:-86]
        logging.info("[+] Swarm hash value: 0x%s", swarm_hash)
        logging.info("[+] Swarm hash removed")
    return bytecode_hex


class EvmDisassembler(Disassembler):

    def __init__(self, bytecode=None):
        Disassembler.__init__(self, asm=EVM(), bytecode=bytecode)

    def disassemble_opcode(self, bytecode, offset=0):
        """
        TODO
        """

        wallet = io.BytesIO(bytecode)
        opcode = int.from_bytes(wallet.read(1), byteorder='big')

        # default value
        invalid = ('INVALID', 0, 0, 0, 0, 'Unknown opcode')
        name, operand_size, pops, pushes, gas, description = \
            self.asm.table.get(opcode, invalid)
        instruction = EvmInstruction(opcode, name, operand_size, pops, pushes,
                                     gas, description, offset=offset)
        if instruction.has_operand:
            instruction.operand = wallet.read(operand_size)
            if instruction.is_push:
                # directly calculate the operand int representation
                instruction.operand_interpretation = \
                    int.from_bytes(instruction.operand, byteorder='big')

        return instruction

    def disassemble(self, bytecode=None, offset=0, r_format='list',
                    analysis=True):
        '''
        TODO
        '''

        self.bytecode = str(bytecode) if bytecode else str(self.bytecode)

        if analysis:
            self.bytecode = runtime_code_detector(self.bytecode)
            self.bytecode = swarm_hash_detector(self.bytecode)

        self.instructions = list()
        self.reverse_instructions = dict()

        return super().disassemble(self.bytecode, offset,
                                   r_format)
