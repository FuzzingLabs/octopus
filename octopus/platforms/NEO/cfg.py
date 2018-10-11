from octopus.core.function import Function
from octopus.core.basicblock import BasicBlock
from octopus.core.edge import Edge
from octopus.core.edge import (EDGE_UNCONDITIONAL,
                               EDGE_CONDITIONAL_TRUE,
                               EDGE_CONDITIONAL_FALSE,
                               EDGE_FALLTHROUGH)

from octopus.analysis.cfg import CFG

from octopus.platforms.NEO.disassembler import NeoDisassembler

from logging import getLogger
logging = getLogger(__name__)


def enum_func_static(instructions):

    functions = list()

    # first function of NeoContract is *usually* the Main function
    function = Function(instructions[0].offset, start_instr=instructions[0], name='Main')

    # parse the instructions and create Function object
    new_func = False
    for inst in instructions:
        if new_func:
            name = 'func_%x' % inst.offset
            function = Function(inst.offset, start_instr=inst, name=name)
            new_func = False

        # associate current instruction to the function
        # Worked because instruction between
        # function.start_offset and function.end_offset
        # are on the same function on Neo
        # i.e linear disassembly
        function.instructions.append(inst)

        # terminator instruction or last one
        if inst.is_halt or inst == instructions[-1]:
            function.size = inst.offset_end - function.start_offset
            function.end_offset = inst.offset_end
            function.end_instr = inst

            functions.append(function)
            new_func = True

    return functions


def xref_of_instr(instr):
    """ Return xref for branch instruction """
    return int.from_bytes(instr.operand, byteorder='little', signed=True) + instr.offset_end - 2


def enumerate_xref(instructions):
    # list cross reference to Instruction and return list of xref
    xrefs = []

    for inst in instructions:
        if inst.is_branch_unconditional:
            xrefs.append(xref_of_instr(inst))
        elif inst.is_branch_conditional:
            xrefs.append(xref_of_instr(inst))
            xrefs.append(inst.offset_end + 1)
        elif inst.is_halt and inst != instructions[-1]:
            xrefs.append(inst.offset_end + 1)
    xrefs = list(set(xrefs))
    return xrefs


def assign_blocks_to_func(basicblocks, functions):

    for func in functions:
        for bb in basicblocks:
            if bb.start_offset in range(func.start_offset, func.end_offset):
                func.basicblocks.append(bb)
    return functions


def enum_blocks_edges(instructions):

    """
    Return a list of basicblock after
    statically parsing given instructions
    """

    basicblocks = list()
    edges = list()
    xrefs = enumerate_xref(instructions)
    # create the first block
    new_block = True

    for inst in instructions:
        if new_block:
            block = BasicBlock(start_offset=inst.offset,
                               start_instr=inst,
                               name='block_%x' % inst.offset)
            new_block = False

        # add current instruction to the basicblock
        block.instructions.append(inst)

        # next instruction in xrefs list
        if (inst.offset_end + 1) in xrefs:
            # absolute JUMP
            if inst.is_branch_unconditional:
                edges.append(Edge(block.name, 'block_%x' % xref_of_instr(inst),
                                  EDGE_UNCONDITIONAL))
            # conditionnal JUMPI / JUMPIF / ...
            elif inst.is_branch_conditional:
                edges.append(Edge(block.name, 'block_%x' % xref_of_instr(inst),
                                  EDGE_CONDITIONAL_TRUE))
                edges.append(Edge(block.name, 'block_%x' % (inst.offset_end + 1),
                                  EDGE_CONDITIONAL_FALSE))
            # Halt instruction : RETURN, STOP, RET, ...
            elif inst.is_halt:
                pass
            # just falls to the next instruction
            else:
                edges.append(Edge(block.name, 'block_%x' % (inst.offset_end + 1),
                                  EDGE_FALLTHROUGH))

            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True

    # add the last block
    basicblocks.append(block)
    edges = list(set(edges))

    return (basicblocks, edges)


class NeoCFG(CFG):

    def __init__(self, bytecode=None, instructions=None, static_analysis=True):
        """ TODO """

        if not bytecode and not instructions:
            raise Exception("No bytecode/instructions provided")
        if instructions:
            self.instructions = instructions
        else:
            # disassemble bytecode to instructions
            disasm = NeoDisassembler(bytecode)
            self.instructions = disasm.disassemble()
        self.static_analysis = static_analysis

        self.basicblocks = list()
        self.functions = list()
        self.edges = list()

        if self.static_analysis:
            self.run_static_analysis()

    def run_static_analysis(self):
        self.functions = enum_func_static(self.instructions)
        self.basicblocks, self.edges = enum_blocks_edges(self.instructions)
        self.functions = assign_blocks_to_func(self.basicblocks, self.functions)

    def __str__(self):
        line = ("length functions = %d\n" % len(self.functions))
        line += ("length basicblocks = %d\n" % len(self.basicblocks))
        line += ("length instructions = %d\n" % len(self.instructions))
        line += ("length edges = %d\n" % len(self.edges))
        return line
