import io
import logging
import re

from octopus.engine.disassembler import Disassembler

from octopus.arch.evm.instruction import EvmInstruction
from octopus.arch.evm.evm import EVM


class EvmDisassembler(Disassembler):

    def __init__(self, bytecode=None):
        Disassembler.__init__(self, asm=EVM(), bytecode=bytecode)
        self.loader_code = None
        self.swarm_hash = None
        self.constructor_args = None

    def runtime_code_detector(self):
        '''Check for presence of runtime code
        '''
        result = list(re.finditer('60.{2}604052', self.bytecode))
        if len(result) > 1:
            position = result[1].start()
            logging.info("[+] Runtime code detected")
            self.loader_code = self.bytecode[:position]
            self.bytecode = self.bytecode[position:]

    def swarm_hash_detector(self):
        '''Check for presence of Swarm hash at the end of bytecode
            https://github.com/ethereum/wiki/wiki/Swarm-Hash
        '''
        #swarm_hash_off = self.bytecode.find('a165627a7a72.*0029')
        result = list(re.finditer('a165627a7a7230.*0029', self.bytecode))
        # bzzr == 0x65627a7a72

        if len(result) > 0:
            swarm_hash_off = result[-1].start()
            swarm_hash_end = result[-1].end()
            if swarm_hash_off > 0:
                logging.info("[+] Swarm hash detected in bytecode")
                self.swarm_hash = self.bytecode[swarm_hash_off:swarm_hash_end]
                logging.info("[+] Swarm hash value: 0x%s", self.swarm_hash)

                # there is possibly constructor argument
                # if there is swarm storage
                if swarm_hash_end != len(self.bytecode):
                    self.constructor_args = self.bytecode[swarm_hash_end:]
                    logging.info("[+] Constructor arguments detected in bytecode")
                    logging.info("[+] Constructor arguments removed from bytecode")
                logging.info("[+] Swarm hash removed from bytecode")
                self.bytecode = self.bytecode[:swarm_hash_off]

    def analysis(self):
        self.runtime_code_detector()
        self.swarm_hash_detector()

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
        creation code remove if analysis param is set to True (default)
        r_format: ('list' | 'text' | 'reverse')
        '''

        self.bytecode = bytecode if bytecode else self.bytecode

        if analysis:
            self.analysis()

        # reset lists
        self.instructions = list()
        self.reverse_instructions = dict()

        # call generic Disassembler.disassemble method
        return super().disassemble(self.bytecode, offset,
                                   r_format)
