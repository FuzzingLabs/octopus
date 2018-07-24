from octopus.core.function import Function
from octopus.core.basicblock import BasicBlock
from octopus.core.edge import (Edge,
                               EDGE_UNCONDITIONAL,
                               EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
                               EDGE_FALLTHROUGH, EDGE_CALL)
from octopus.analysis.cfg import CFG

from octopus.arch.wasm.analyzer import WasmModuleAnalyzer
from octopus.arch.wasm.disassembler import WasmDisassembler
from octopus.arch.wasm.format import (format_func_name,
                                      format_bb_name)


from octopus.core.utils import bytecode_to_bytes
import logging

from wasm.compat import byte2int

# for graph visualisation
from graphviz import Digraph
DESIGN_IMPORT = {'fillcolor': 'turquoise',
                 'shape': 'box',
                 'style': 'filled'}

DESIGN_EXPORT = {'fillcolor': 'grey',
                 'shape': 'box',
                 'style': 'filled'}

log = logging.getLogger(__name__)
log.setLevel(level=logging.WARNING)


def enum_func(module_bytecode):
    ''' return a list of Function
        see:: octopus.core.function
    '''
    functions = list()
    analyzer = WasmModuleAnalyzer(module_bytecode)

    protos = analyzer.func_prototypes
    import_len = len(analyzer.imports_func)

    for idx, code in enumerate(analyzer.codes):
        # get corresponding function prototype
        name, param_str, return_str = protos[import_len + idx]

        name = format_func_name(name, param_str, return_str)
        instructions = WasmDisassembler().disassemble(code)
        cur_function = Function(0, instructions[0], name=name)
        cur_function.instructions = instructions

        functions.append(cur_function)
    return functions


def enum_func_call_edges(functions, len_imports):
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
                # The `call_indirect` operator takes a list of function arguments and as the last operand the index into the table.
                elif inst.name == "call_indirect":
                    # the last operand is the index on the table
                    node_to = int(inst.operand_interpretation.split(',')[-1].split(' ')[-1])
                call_edges.append((node_from, node_to))

    return call_edges


def enum_blocks_edges(function_id, instructions):

    """
    Return a list of basicblock after
    statically parsing given instructions
    """

    basicblocks = list()
    edges = list()

    branches = []
    xrefs = []

    intent = 0
    blocks_tmp = []
    blocks_list = []
    # remove last instruction that is 'end' for the funtion
    #tt = instructions[:-1]
    for index, inst in enumerate(instructions[:-1]):

        if inst.is_block_terminator:
            start, name = blocks_tmp.pop()
            if inst.name == 'else':
                end = inst.offset - 1
            else:
                end = inst.offset_end
            blocks_list.append((intent, start, end, name))
            intent -= 1
        if inst.is_block_starter:  # in ['block', 'loop']:
            blocks_tmp.append((inst.offset, inst.name))
            intent += 1
        if inst.is_branch:
            branches.append((intent, inst))

    # add function body end
    blocks_list.append((0, 0, instructions[-1].offset_end, 'func'))
    blocks_list = sorted(blocks_list, key=lambda tup: (tup[1], tup[0]))

    for depth, inst in branches:
        labl = list()
        if inst.name == 'br_table':
            labl = [i for i in inst.insn_byte[2:]]
        else:
            labl.append(int(inst.operand_interpretation.split(' ')[-1]))

        for d2 in labl:
            rep = next(((i, s, e, n) for i, s, e, n in blocks_list if (i == (depth - d2) and s < inst.offset and e > inst.offset_end)), None)
            if rep:
                i, start, end, name = rep
                if name == 'loop':
                    value = start  # else name == 'block'
                elif name == 'block' or name == 'func':
                    value = end
                else:
                    value = None
                inst.xref.append(value)
                xrefs.append(value)

    # remove "block" instruction - not usefull graphicaly
    # instructions = [x for x in instructions if x.name not in ['block', 'loop']]

    # enumerate blocks

    new_block = True

    for index, inst in enumerate(instructions):

        # creation of a block
        if new_block:
            block = BasicBlock(inst.offset,
                               inst,
                               name=format_bb_name(function_id, inst.offset))
            new_block = False

        # add current instruction to the basicblock
        block.instructions.append(inst)

        # next instruction is a jump target
        if index < (len(instructions) - 1) and \
           instructions[index + 1].offset in xrefs:
            new_block = True
        # absolute jump - br
        elif inst.is_branch_unconditional:
            new_block = True
        # conditionnal jump - br_if
        elif inst.is_branch_conditional:
            new_block = True
        # end of a block
        elif index < (len(instructions) - 1) and \
                inst.name in ['end']:  # is_block_terminator
            new_block = True
        #elif index < (len(instructions) - 1) and \
        #        instructions[index + 1].name == 'else':  # is_block_terminator
        #    new_block = True
        # start of a block
        elif index < (len(instructions) - 1) and \
                instructions[index + 1].is_block_starter:
            new_block = True
        # last instruction of the bytecode
        elif inst.offset == instructions[-1].offset:
            new_block = True

        if new_block:
            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True

    # TODO: detect and remove end instruction that end loop

    # enumerate edges
    for index, block in enumerate(basicblocks):
        # get the last instruction
        inst = block.end_instr
        # unconditional jump - br
        if inst.is_branch_unconditional:
            for ref in inst.xref:
                edges.append(Edge(block.name, format_bb_name(function_id, ref), EDGE_UNCONDITIONAL))
        # conditionnal jump - br_if, if
        elif inst.is_branch_conditional:
            if inst.name == 'if':
                edges.append(Edge(block.name,
                             format_bb_name(function_id, inst.offset_end + 1),
                             EDGE_CONDITIONAL_TRUE))
                g_block = next(iter([b for b in blocks_list if b[1] == inst.offset]), None)
                jump_target = g_block[2] + 1
                edges.append(Edge(block.name,
                             format_bb_name(function_id, jump_target),
                             EDGE_CONDITIONAL_FALSE))
            else:
                for ref in inst.xref:
                    if ref != inst.offset_end + 1:
                        edges.append(Edge(block.name,
                                          format_bb_name(function_id, ref),
                                          EDGE_CONDITIONAL_TRUE))
                edges.append(Edge(block.name,
                             format_bb_name(function_id, inst.offset_end + 1),
                             EDGE_CONDITIONAL_FALSE))
        elif inst.offset != instructions[-1].offset:
            # EDGE_FALLTHROUGH
            edges.append(Edge(block.name, format_bb_name(function_id, inst.offset_end + 1), EDGE_FALLTHROUGH))

    # prevent duplicate edges
    edges = list(set(edges))
    return basicblocks, edges


class WasmCFG(CFG):
    """
    TODO: fix some CFG issue related to br_table instruction
    """
    def __init__(self, module_bytecode, static_analysis=True):

        self.module_bytecode = bytecode_to_bytes(module_bytecode)
        self.static_analysis = static_analysis
        self.analyzer = None

        self.functions = list()
        self.basicblocks = list()
        self.edges = list()

        if self.static_analysis:
            self.analyzer = WasmModuleAnalyzer(self.module_bytecode)
            self.run_static_analysis()

    def run_static_analysis(self):
        self.functions = enum_func(self.module_bytecode)

        for idx, func in enumerate(self.functions):
            func.basicblocks, edges = enum_blocks_edges(idx, func.instructions)
            # all bb name are unique so we can create global bb & edge list
            self.basicblocks += func.basicblocks
            self.edges += edges

    def get_functions_call_edges(self, format_fname=True):

        nodes = list()
        edges = list()

        if not self.analyzer:
            self.analyzer = WasmModuleAnalyzer(self.module_bytecode)
        if not self.functions:
            self.functions = enum_func(self.module_bytecode)

        # create nodes
        for name, param_str, return_str in self.analyzer.func_prototypes:
            if format_fname:
                nodes.append(format_func_name(name, param_str, return_str))
            else:
                nodes.append(name)

        log.info('nodes: %s', nodes)

        # create edges
        tmp_edges = enum_func_call_edges(self.functions,
                                         len(self.analyzer.imports_func))

        # tmp_edges = [(node_from, node_to), (...), ...]
        for node_from, node_to in tmp_edges:
            # node_from
            name, param, ret = self.analyzer.func_prototypes[node_from]
            if format_fname:
                from_final = format_func_name(name, param, ret)
            else:
                from_final = name
            # node_to
            name, param, ret = self.analyzer.func_prototypes[node_to]
            to_final = format_func_name(name, param, ret)
            if format_fname:
                to_final = format_func_name(name, param, ret)
            else:
                to_final = name
            edges.append(Edge(from_final, to_final, EDGE_CALL))
        log.info('edges: %s', edges)

        return (nodes, edges)

    def visualize_call_flow(self, filename="wasm_call_graph_octopus.gv"):

        nodes, edges = self.get_functions_call_edges(format_fname=False)

        g = Digraph(filename, filename=filename)
        g.attr(rankdir='LR')

        with g.subgraph(name='global') as c:

            export_list = [d['field_str'] for d in self.analyzer.exports]
            import_list = [x for _, x, _ in self.analyzer.imports_func]
            # create all the graph nodes (function name)
            for idx, node in enumerate(nodes):
                if node in import_list:
                    log.debug('import ' + node)
                    fillcolor = DESIGN_IMPORT.get('fillcolor')
                    shape = DESIGN_IMPORT.get('shape')
                    style = DESIGN_IMPORT.get('style')
                    c.node(node, fillcolor=fillcolor, shape=shape, style=style)
                elif node in export_list:
                    log.debug('export ' + node)
                    fillcolor = DESIGN_EXPORT.get('fillcolor')
                    shape = DESIGN_EXPORT.get('shape')
                    style = DESIGN_EXPORT.get('style')
                    c.node(node, fillcolor=fillcolor, shape=shape, style=style)
                else:
                    c.node(node)

            # check if multiple same edges
            # in that case, put the number into label
            edges_counter = dict((x, edges.count(x)) for x in set(edges))
            # insert edges on the graph
            for edge, count in edges_counter.items():
                label = None
                if count > 1:
                    label = str(count)
                c.edge(edge.node_from, edge.node_to, label=label)

        g.render(filename, view=True)
