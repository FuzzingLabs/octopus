from octopus.api.cfg import CFG
from octopus.api.function import Function
from octopus.api.basicblock import BasicBlock
from octopus.api.basicblock import (BASICBLOCK_TERMINAL,
                                    BASICBLOCK_UNCONDITIONAL,
                                    BASICBLOCK_CONDITIONAL,
                                    BASICBLOCK_FALLTHROUGH,
                                    BASICBLOCK_DEFAULT)

from octopus.platforms.ETH.disassembler import EthereumDisassembler

import logging
import json
import os


log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)


SIGNATURE_FILE_PATH = '/utils/signatures.txt'


def enumerate_functions_statically(instructions):

    functions = list()

    # first function is *usually* the function dispatcher
    function = Function(start_offset=0,
                        start_instr=instructions[0],
                        name='Dispatcher',
                        prefered_name='Dispatcher')
    functions.append(function)

    # parse the instructions and create Function object
    for inst in instructions:
        try:
            # PUSH4 are used to push the function signature on the stack
            if inst.name == 'PUSH4':
                index = instructions.index(inst)
                list_inst = instructions[index:index + 4]
                push4, eq, push, jumpi = list_inst[0], list_inst[1], list_inst[2], list_inst[3]

                # check if this basicblock test function signature
                if eq.name == 'EQ' and push.name in ['PUSH1', 'PUSH2'] and jumpi.name == 'JUMPI':
                    xref = int.from_bytes(push.operand, byteorder='big')
                    sign = int.from_bytes(push4.operand, byteorder='big')
                    name = 'func_%x' % sign
                    prefered_name = find_signature(sign)

                    # find instr with offset == xref
                    begin_function = next(filter(lambda i: i.offset == xref, instructions))
                    # create new function
                    function = Function(xref,
                                        start_instr=begin_function,
                                        name=name,
                                        prefered_name=prefered_name)

                    functions.append(function)
        except:
            log.info('enumerate_functions_statically Exception')
            pass
    return functions


def find_signature(sign):
    path = os.path.dirname(os.path.realpath(__file__)) + SIGNATURE_FILE_PATH
    with open(path) as data_file:
        data = json.load(data_file)
    try:
        pref_name = data[str(hex(sign))]
        return pref_name
    except:
        pass
    return None


def enumerate_basicblocks_statically(instructions):

    """
    Return a list of basicblock after
    statically parsing given instructions
    """

    basicblocks = list()
    index = 0

    # create the first block
    new_block = False
    block = BasicBlock(instructions[0].offset,
                       instructions[0],
                       name='block_%x' % instructions[0].offset)

    for inst in instructions:
        if new_block:
            block = BasicBlock(inst.offset,
                               inst,
                               name='block_%x' % inst.offset)
            new_block = False

        # add current instruction to the basicblock
        block.instructions.append(inst)

        # absolute JUMP
        if inst.is_branch_unconditional:
            block.type = BASICBLOCK_UNCONDITIONAL
            logging.debug("unconditional %x : %s", inst.offset, inst.name)

        # conditionnal JUMPI
        elif inst.is_branch_conditional:
            block.type = BASICBLOCK_CONDITIONAL
            logging.debug("conditional %x : %s", inst.offset, inst.name)

        # Halt instruction : RETURN, STOP, ...
        elif inst.is_halt:  # and inst != instructions[-1]:
            block.type = BASICBLOCK_TERMINAL
            logging.debug("terminal %x : %s", inst.offset, inst.name)

        # just falls to the next instruction
        elif inst != instructions[-1] and \
                instructions[index + 1].name == 'JUMPDEST':
            block.type = BASICBLOCK_FALLTHROUGH
            logging.debug("fallthrough %x : %s", inst.offset, inst.name)

        # last instruction of the entire bytecode
        elif inst == instructions[-1]:
            block.type = BASICBLOCK_TERMINAL

        if block.type != BASICBLOCK_DEFAULT:
            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True

        index += 1

    return basicblocks


class EthereumCFG(CFG):

    def __init__(self, bytecode=None, instructions=None, analysis='dynamic'):
        """ TODO """

        if not bytecode and not instructions:
            raise Exception("No bytecode/instructions provided")
        if instructions:
            self.instructions = instructions
        else:
            # disassemble bytecode to instructions
            disasm = EthereumDisassembler(bytecode)
            self.instructions = disasm.disassemble()
        self.analysis = analysis

        self.basicblocks = list()
        self.functions = list()
        self.edges = list()

        if self.analysis == 'dynamic':
            self.run_dynamic_analysis()
        elif self.analysis == 'static':
            self.run_static_analysis()

    def run_static_analysis(self):
        self.functions = enumerate_functions_statically(self.instructions)
        self.basicblocks = enumerate_basicblocks_statically(self.instructions)

    def run_dynamic_analysis(self):

        from octopus.platforms.ETH.ssa import EthereumSSAEngine

        emul = EthereumSSAEngine(instructions=self.instructions)
        emul.emulate()
        self.functions = emul.functions
        self.basicblocks = emul.basicblocks
        self.edges = emul.edges

    def details(self):
        print("len bb = %d" % len(self.basicblocks))
        print("len func = %d" % len(self.functions))
        print("len instructions = %d" % len(self.instructions))
        print("len edges = %d" % len(self.edges))

    """
    def assignXrefForInstruction(self):
        ''' return list of beginning offset for Basic block '''

        # remove potential older analysis result
        self.xrefs = []
        last_push = None

        for inst in self.instructions:

            # second case - relative jump : PUSH1/2 and JUMP/I
            if inst.is_branch and last_push is not None:
                inst.set_xref(last_push.operand)
                self.xrefs.append(inst.xref)
                self.xrefs.append(inst.offset_end + 1)
                last_push = None

            # first case : inst in ['RETURN', 'STOP', 'INVALID', 'JUMP', 'JUMPI', 'SELFDESTRUCT', 'REVERT']
            if inst.is_terminator:
                self.xrefs.append(inst.offset_end + 1)
                last_push = None

            # usually describe as basicblock delimiter
            if inst.name == 'JUMPDEST':
                self.xrefs.append(inst.offset)

            # save last push for the second case
            if inst.name in ['PUSH1', 'PUSH2']:
                last_push = inst
            else:
                last_push = None
        self.xrefs = list(set(self.xrefs))
        return self.xrefs
    """
