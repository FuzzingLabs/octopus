from octopus.api.function import Function
from octopus.api.basicblock import BasicBlock
from octopus.api.edge import Edge
from octopus.api.edge import (EDGE_UNCONDITIONAL,
                              EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
                              EDGE_FALLTHROUGH, EDGE_CALL)
from octopus.api.cfg import CFG
from octopus.api.wasm.analyzer import WasmModuleAnalyzer

from octopus.platforms.EOS.disassembler import EosDisassembler

import logging
log = logging.getLogger(__name__)
log.setLevel(level=logging.WARNING)


def format_func_name(name, param_str, return_str):
    result = "%s " % return_str if return_str else ""
    return ('%s%s(%s)' % (result, name, param_str))


def format_bb_name(function_id, offset):
    return ('block_%x_%x' % (function_id, offset))


def enumerate_functions(module_bytecode):

    functions = list()
    analyzer = WasmModuleAnalyzer(module_bytecode)

    protos = analyzer.func_prototypes
    import_len = len(analyzer.imports_func)

    for idx, code in enumerate(analyzer.codes):
        # get corresponding function prototype
        name, param_str, return_str = protos[import_len + idx]

        name = format_func_name(name, param_str, return_str)
        instructions = EosDisassembler().disassemble(code)
        cur_function = Function(0, instructions[0], name=name)
        cur_function.instructions = instructions

        functions.append(cur_function)
    return functions


def enumerate_functions_call_edges(functions, len_imports):
    ''' return a list of tuple with
        (index_func_node_from, index_func_node_to)
    '''
    call_edges = list()

    # iterate over functions
    for index, func in enumerate(functions):
        node_from = len_imports + index
        # iterates over instruction
        for inst in func.instructions:
            # detect if inst is a call instructions
            if inst.is_call:
                log.info('%s', inst.operand_interpretation)
                if inst.name == "call":
                    # only get the import_id
                    node_to = int(inst.operand_interpretation.split(' ')[1])
                elif inst.name == "call_indirect":
                    # the last operand is the index on the table
                    node_to = int(inst.operand_interpretation.split(',')[-1].split(' ')[-1])
                call_edges.append((node_from, node_to))

    return call_edges


def enumerate_basicblocks_edges(function_id, instructions):

    """
    Return a list of basicblock after
    statically parsing given instructions
    """

    basicblocks = list()
    edges = list()
    labels = []

    intent = 0
    # find label first
    for index, inst in enumerate(instructions):
        if inst.is_block_starter:
            if inst.name in ['block', 'loop']:
                intent += 1
        elif inst.name in ['end']:
            if intent > 0:
                intent -= 1
                #tmp_labels.append({'intent': intent,
                #                   'offset': inst.offset_end})
                labels.append(inst.offset_end)
    # print(function_id)
    # print(labels)
    '''
    #e = [{'intent': 0, 'offset': 15}, {'intent': 1, 'offset': 17}, {'intent': 0, 'offset': 56}]
    tmp_list = []
    for index, x in enumerate(tmp_labels):
        if x.get('intent') == 0:
            labels += tmp_list[::-1]
            tmp_list = []
        tmp_list.append(x.get('offset'))
    labels += tmp_list[::-1]
    print(labels)
    '''

    # remove "block" instruction - not usefull graphicaly
    instructions = [x for x in instructions if x.name not in ['block', 'loop']]
    # create the first block
    new_block = False
    end_block = False
    block = BasicBlock(instructions[0].offset,
                       instructions[0],
                       name=format_bb_name(function_id, instructions[0].offset))

    for index, inst in enumerate(instructions):
        if new_block:
            block = BasicBlock(inst.offset,
                               inst,
                               name=format_bb_name(function_id, inst.offset))
            new_block = False

        # add current instruction to the basicblock
        block.instructions.append(inst)

        # absolute jump - br
        # br is *always* followed by end instruction
        if inst.is_branch_unconditional:
            end_block = True
            jump_offset = int(inst.operand_interpretation.split(' ')[1])
            if instructions[index + 1].name == 'end':
                end_block = False
            edges.append(Edge(block.name, format_bb_name(function_id, labels[jump_offset]  + 1), EDGE_UNCONDITIONAL))

        # conditionnal jump - br_if
        elif inst.is_branch_conditional:
            end_block = True
            jump_offset = int(inst.operand_interpretation.split(' ')[1])
            edges.append(Edge(block.name, format_bb_name(function_id, labels[jump_offset] + 1), EDGE_CONDITIONAL_TRUE))
            edges.append(Edge(block.name, format_bb_name(function_id, instructions[index + 1].offset), EDGE_CONDITIONAL_FALSE))

        # end of a block
        elif index < (len(instructions) - 1) and \
                inst.name in ['end', 'else']:  # is_block_terminator
            end_block = True
            if not instructions[index - 1].is_branch_unconditional:
                edges.append(Edge(block.name, format_bb_name(function_id, instructions[index + 1].offset), EDGE_FALLTHROUGH))

        # start of a block
        elif index < (len(instructions) - 1) and \
                instructions[index + 1].is_block_starter:
            end_block = True
            edges.append(Edge(block.name, format_bb_name(function_id, instructions[index + 1].offset), EDGE_FALLTHROUGH))

        # last instruction of the entire bytecode
        elif inst == instructions[-1]:
            end_block = True

        if end_block:
            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True
            end_block = False

    edges = list(set(edges))
    return basicblocks, edges


class EosCFG(CFG):
    """
    TODO: fix some CFG issue related to block/end/if/else/end instructions
    """
    def __init__(self, module_bytecode, static_analysis=True):

        self.module_bytecode = module_bytecode
        self.static_analysis = static_analysis
        self.analyzer = None

        self.functions = list()
        self.basicblocks = list()
        self.edges = list()

        if self.static_analysis:
            self.analyzer = WasmModuleAnalyzer(self.module_bytecode)
            self.run_static_analysis()

    def run_static_analysis(self):
        self.functions = enumerate_functions(self.module_bytecode)

        for idx, func in enumerate(self.functions):
            func.basicblocks, edges = enumerate_basicblocks_edges(idx, func.instructions)
            # all bb name are unique so we can create global bb & edge list
            self.basicblocks += func.basicblocks
            self.edges += edges

    def get_functions_call_edges(self):

        nodes = list()
        edges = list()

        if not self.analyzer:
            self.analyzer = WasmModuleAnalyzer(self.module_bytecode)
        if not self.functions:
            self.functions = enumerate_functions(self.module_bytecode)

        # create nodes
        for name, param_str, return_str in self.analyzer.func_prototypes:
            nodes.append(format_func_name(name, param_str, return_str))
        log.info('nodes: %s', nodes)

        # create edges
        tmp_edges = enumerate_functions_call_edges(self.functions,
                                                   len(self.analyzer.imports_func))

        # tmp_edges = [(node_from, node_to), (...), ...]
        for node_from, node_to in tmp_edges:
            # node_from
            name, param, ret = self.analyzer.func_prototypes[node_from]
            from_final = format_func_name(name, param, ret)
            # node_to
            name, param, ret = self.analyzer.func_prototypes[node_to]
            to_final = format_func_name(name, param, ret)
            edges.append(Edge(from_final, to_final, EDGE_CALL))
        log.info('edges: %s', edges)

        return (nodes, edges)

    def show(self):
        print("len func = %d" % len(self.functions))
        print("len edges = %d" % len(self.edges))
