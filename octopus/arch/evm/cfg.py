from octopus.analysis.cfg import CFG
from octopus.analysis.graph import CFGGraph
from octopus.core.function import Function
from octopus.core.basicblock import BasicBlock

from octopus.arch.evm.disassembler import EvmDisassembler

import json
import os

from logging import getLogger
logging = getLogger(__name__)


SIGNATURE_FILE_PATH = '/signatures.json'


def enum_func_static(instructions):

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
            logging.warning('enum_func_static Exception')
            pass
    return functions


def find_signature(sign):
    path = os.path.dirname(os.path.realpath(__file__)) + SIGNATURE_FILE_PATH
    with open(path) as data_file:
        data = json.load(data_file)

    list_name = [name for name, hexa in data.items() if hexa == str(hex(sign))]

    if len(list_name) > 1:
        logging.warning('function signatures collision: %s', list_name)
        return '_or_'.join(list_name)
    elif list_name:
        return list_name[0]
    else:
        return None


def enum_blocks_static(instructions):

    """
    Return a list of basicblock after
    statically parsing given instructions
    """

    basicblocks = list()
    index = 0

    # create the first block
    new_block = False
    end_block = False
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
            new_block = True

        # conditionnal JUMPI
        elif inst.is_branch_conditional:
            new_block = True

        # Halt instruction : RETURN, STOP, ...
        elif inst.is_halt:  # and inst != instructions[-1]:
            new_block = True

        # just falls to the next instruction
        elif inst != instructions[-1] and \
                instructions[index + 1].name == 'JUMPDEST':
            new_block = True

        # last instruction of the entire bytecode
        elif inst == instructions[-1]:
            end_block = True

        if new_block or end_block:
            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True
            end_block = False

        index += 1

    return basicblocks

'''
def enum_calls(instructions):
    for inst in instructions:
        # inst is a call instruction and ssa repr is not null
        if inst.is_call and inst.ssa:
            to_addr = inst.ssa.args[1]
            print('%s to %s' % (inst.name, str(to_addr)))
'''


class EvmCFG(CFG):

    def __init__(self, bytecode=None, analysis='dynamic'):
        """ TODO """

        self.bytecode = bytecode
        self.disasm = EvmDisassembler(self.bytecode)
        self.instructions = self.disasm.disassemble()
        self.analysis = analysis

        self.basicblocks = list()
        self.functions = list()
        self.edges = list()

        if self.analysis == 'dynamic':
            self.run_dynamic_analysis()
        elif self.analysis == 'static':
            self.run_static_analysis()

    def run_static_analysis(self):
        self.functions = enum_func_static(self.instructions)
        self.basicblocks = enum_blocks_static(self.instructions)

    def run_dynamic_analysis(self):

        from octopus.platforms.ETH.emulator import EvmSSAEngine

        emul = EvmSSAEngine(self.bytecode)
        emul.emulate()
        self.functions = emul.functions
        self.basicblocks = emul.basicblocks
        self.edges = emul.edges

    def visualize(self, simplify=False, ssa=False):
        """Visualize the cfg
        used CFGGraph
        equivalent to:
            graph = CFGGraph(cfg)
            graph.view_functions()
        """
        graph = CFGGraph(self)
        graph.view(simplify=simplify, ssa=ssa)

    def __str__(self):
        line = ("length functions = %d\n" % len(self.functions))
        line += ("length basicblocks = %d\n" % len(self.basicblocks))
        line += ("length instructions = %d\n" % len(self.instructions))
        line += ("length edges = %d\n" % len(self.edges))
        return line
