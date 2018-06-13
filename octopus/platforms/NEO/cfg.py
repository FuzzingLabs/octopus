from octopus.api.function import Function
from octopus.api.basicblock import BasicBlock
from octopus.api.basicblock import (BASICBLOCK_TERMINAL,
                                    BASICBLOCK_UNCONDITIONAL,
                                    BASICBLOCK_CONDITIONAL,
                                    BASICBLOCK_FALLTHROUGH)
from octopus.api.edge import Edge
from octopus.api.edge import (EDGE_UNCONDITIONAL,
                              EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
                              EDGE_FALLTHROUGH)

from octopus.api.cfg import CFG

from octopus.platforms.NEO.disassembler import NeoDisassembler

import logging
logging.basicConfig(level=logging.INFO)


def enumerate_functions_statically(instructions):

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


def enumerate_edges_statically(basicblocks):

    edges = list()

    for block in basicblocks:
        # JMP
        if block.is_unconditional:
            jmp_instr = block.end_instr
            edges.append(Edge(block.name, 'block_%x' % xref_of_instr(jmp_instr), EDGE_UNCONDITIONAL))

        # JMPIF, JMPIFNOT
        elif block.is_conditional:
            jmp_instr = block.end_instr
            edges.append(Edge(block.name, 'block_%x' % xref_of_instr(jmp_instr), EDGE_CONDITIONAL_TRUE))
            edges.append(Edge(block.name, 'block_%x' % (block.end_offset + 1), EDGE_CONDITIONAL_FALSE))

        elif block.is_fallthrough:
            edges.append(Edge(block.name, 'block_%x' % (block.end_offset + 1), EDGE_FALLTHROUGH))

    edges = list(set(edges))
    return edges


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


def assign_basicblocks_to_functions(basicblocks, functions):

    for func in functions:
        for bb in basicblocks:
            if bb.start_offset in range(func.start_offset, func.end_offset):
                func.basicblocks.append(bb)
    return functions


def enumerate_basicblocks_statically(instructions):

    """
    Return a list of basicblock after
    statically parsing given instructions
    """

    basicblocks = list()
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

        # next instruction in list_ref
        if (inst.offset_end + 1) in xrefs:
            # absolute JUMP
            if inst.is_branch_unconditional:
                block.type = BASICBLOCK_UNCONDITIONAL
                logging.debug("unconditional %x : %s", inst.offset, inst.name)
            # conditionnal JUMPI / JUMPIF / ...
            elif inst.is_branch_conditional:
                block.type = BASICBLOCK_CONDITIONAL
                logging.debug("conditional %x : %s", inst.offset, inst.name)
            # Halt instruction : RETURN, STOP, RET, ...
            elif inst.is_halt:  # and inst != func.instructions[-1]:
                block.type = BASICBLOCK_TERMINAL
                logging.debug("terminal %x : %s", inst.offset, inst.name)
            # just falls to the next instruction
            else:
                block.type = BASICBLOCK_FALLTHROUGH
                logging.debug("fallthrough %x : %s", inst.offset, inst.name)

            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True

    # add the last block
    basicblocks.append(block)
    basicblocks = list(set(basicblocks))

    return basicblocks


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
        self.functions = enumerate_functions_statically(self.instructions)
        self.basicblocks = enumerate_basicblocks_statically(self.instructions)
        self.functions = assign_basicblocks_to_functions(self.basicblocks, self.functions)
        self.edges = enumerate_edges_statically(self.basicblocks)

    def show(self):
        print("len bb = %d" % len(self.basicblocks))
        print("len func = %d" % len(self.functions))
        print("len instructions = %d" % len(self.instructions))
        print("len edges = %d" % len(self.edges))
