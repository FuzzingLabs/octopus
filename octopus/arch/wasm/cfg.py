# for graph visualisation

from logging import getLogger
from graphviz import Digraph

from octopus.analysis.cfg import CFG
from octopus.analysis.graph import CFGGraph

from octopus.arch.wasm.analyzer import WasmModuleAnalyzer
from octopus.arch.wasm.disassembler import WasmDisassembler
from octopus.arch.wasm.format import (format_bb_name,
                                      format_func_name)
from octopus.arch.wasm.wasm import _groups

from octopus.core.basicblock import BasicBlock
from octopus.core.edge import (Edge,
                               EDGE_UNCONDITIONAL,
                               EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
                               EDGE_FALLTHROUGH, EDGE_CALL)
from octopus.core.function import Function
from octopus.core.utils import bytecode_to_bytes


logging = getLogger(__name__)


DESIGN_IMPORT = {'fillcolor': 'turquoise',
                 'shape': 'box',
                 'style': 'filled'}

DESIGN_EXPORT = {'fillcolor': 'grey',
                 'shape': 'box',
                 'style': 'filled'}


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
        name, param_str, return_str, _ = protos[import_len + idx]

        prefered_name = format_func_name(name, param_str, return_str)
        instructions = WasmDisassembler().disassemble(code)
        cur_function = Function(0, instructions[0], name=name,
                                prefered_name=prefered_name)
        cur_function.instructions = instructions

        functions.append(cur_function)
    return functions


def enum_func_name_call_indirect(functions):
    ''' return a list of function name if they used call_indirect
    '''
    func_name = list()

    # iterate over functions
    for func in functions:
        for inst in func.instructions:
            if inst.name == "call_indirect":
                func_name.append(func.name)
    func_name = list(set(func_name))
    return func_name


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
            if inst.name == "call":  #is_call:
                logging.info('%s', inst.operand_interpretation)
                #if inst.name == "call":
                # only get the import_id
                node_to = int(inst.operand_interpretation.split(' ')[1])
                # The `call_indirect` operator takes a list of function arguments and as the last operand the index into the table.
                #elif inst.name == "call_indirect":
                # the last operand is the index on the table
                #print(inst.operand_interpretation)
                #print(type(inst.insn_byte[1]))
                #node_to = inst.insn_byte[1]
                #node_to = int(inst.operand_interpretation.split(',')[-1].split(' ')[-1])
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

    # we need to do that because jump label are relative to the current block index
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
                # if we branch to a 'loop' label
                # we go at the entry of the 'loop' block
                if name == 'loop':
                    value = start
                # if we branch to a 'block' label
                # we go at the end of the "block" block
                elif name == 'block' or name == 'func':
                    value = end
                # we don't know
                else:
                    value = None
                inst.xref.append(value)
                xrefs.append(value)

    # assign xref for "if" branch
    # needed because 'if' don't used label
    for index, inst in enumerate(instructions[:-1]):
        if inst.name == 'if':
            g_block = next(iter([b for b in blocks_list if b[1] == inst.offset]), None)
            jump_target = g_block[2] + 1
            inst.xref.append(jump_target)
            xrefs.append(jump_target)
        elif inst.name == 'else':
            g_block = next(iter([b for b in blocks_list if b[1] == inst.offset]), None)
            jump_target = g_block[2] + 1
            inst.xref.append(jump_target)
            xrefs.append(jump_target)

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
        # is_block_terminator
        # GRAPHICAL OPTIMIZATION: merge end together
        elif index < (len(instructions) - 1) and \
                instructions[index + 1].name in ['else', 'loop']:  # is_block_terminator
            new_block = True
        # last instruction of the bytecode
        elif inst.offset == instructions[-1].offset:
            new_block = True

        if new_block:
            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True

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
                if_b = next(iter([b for b in blocks_list if b[1] == inst.offset]), None)
                #else_block = blocks_list[blocks_list.index(if_block) + 1]
                jump_target = if_b[2] + 1
                edges.append(Edge(block.name,
                             format_bb_name(function_id, jump_target),
                             EDGE_CONDITIONAL_FALSE))
            else:
                for ref in inst.xref:
                    if ref and ref != inst.offset_end + 1:
                        # create conditionnal true edges
                        edges.append(Edge(block.name,
                                          format_bb_name(function_id, ref),
                                          EDGE_CONDITIONAL_TRUE))
                # create conditionnal false edge
                edges.append(Edge(block.name,
                             format_bb_name(function_id, inst.offset_end + 1),
                             EDGE_CONDITIONAL_FALSE))
        # instruction that end the flow
        elif [i.name for i in block.instructions if i.is_halt]:
            pass
        elif inst.is_halt:
            pass

        # handle the case when you have if and else following
        elif inst.offset != instructions[-1].offset and \
                block.start_instr.name != 'else' and \
                instructions[instructions.index(inst) + 1].name == 'else':

            else_ins = instructions[instructions.index(inst) + 1]
            else_b = next(iter([b for b in blocks_list if b[1] == else_ins.offset]), None)

            edges.append(Edge(block.name, format_bb_name(function_id, else_b[2] + 1), EDGE_FALLTHROUGH))
        # add the last intruction "end" in the last block
        elif inst.offset != instructions[-1].offset:
            # EDGE_FALLTHROUGH
            edges.append(Edge(block.name, format_bb_name(function_id, inst.offset_end + 1), EDGE_FALLTHROUGH))

    # prevent duplicate edges
    edges = list(set(edges))
    return basicblocks, edges


class WasmCFG(CFG):
    """
    """
    def __init__(self, module_bytecode):
        self.module_bytecode = bytecode_to_bytes(module_bytecode)

        self.functions = list()
        self.basicblocks = list()
        self.edges = list()

        self.analyzer = WasmModuleAnalyzer(self.module_bytecode)
        self.run_static_analysis()

    def run_static_analysis(self):
        self.functions = enum_func(self.module_bytecode)

        for idx, func in enumerate(self.functions):
            func.basicblocks, edges = enum_blocks_edges(idx, func.instructions)
            # all bb name are unique so we can create global bb & edge list
            self.basicblocks += func.basicblocks
            self.edges += edges

    def get_function(self, name=None, prefered_name=None):
        if name:
            return [x for x in self.functions if x.name == name][0]
        elif prefered_name:
            return [x for x in self.functions if x.prefered_name == prefered_name][0]
        else:
            raise Exception('name/prefered_name not found, please check again')

    def get_functions_call_edges(self, format_fname=False):

        nodes = list()
        edges = list()

        if not self.analyzer:
            self.analyzer = WasmModuleAnalyzer(self.module_bytecode)
        if not self.functions:
            self.functions = enum_func(self.module_bytecode)

        # create nodes
        for name, param_str, return_str, _ in self.analyzer.func_prototypes:
            if format_fname:
                nodes.append(format_func_name(name, param_str, return_str))
            else:
                nodes.append(name)

        logging.info('nodes: %s', nodes)

        # create edges
        tmp_edges = enum_func_call_edges(self.functions,
                                         len(self.analyzer.imports_func))

        # tmp_edges = [(node_from, node_to), (...), ...]
        for node_from, node_to in tmp_edges:
            # node_from
            name, param, ret, _ = self.analyzer.func_prototypes[node_from]
            if format_fname:
                from_final = format_func_name(name, param, ret)
            else:
                from_final = name
            # node_to
            name, param, ret, _ = self.analyzer.func_prototypes[node_to]
            to_final = format_func_name(name, param, ret)
            if format_fname:
                to_final = format_func_name(name, param, ret)
            else:
                to_final = name
            edges.append(Edge(from_final, to_final, EDGE_CALL))
        logging.info('edges: %s', edges)

        return (nodes, edges)

    def __str__(self):
        line = ("length functions = %d\n" % len(self.functions))
        line += ("length basicblocks = %d\n" % len(self.basicblocks))
        line += ("length edges = %d\n" % len(self.edges))
        return line

    def visualize(self, function=True, simplify=False, ssa=False):
        """Visualize the cfg
        used CFGGraph
        equivalent to:
            graph = CFGGraph(cfg)
            graph.view_functions()
        """
        graph = CFGGraph(self)
        if function:
            graph.view_functions(simplify=simplify, ssa=ssa)
        else:
            graph.view(simplify=simplify, ssa=ssa)

    def visualize_call_flow(self, filename="wasm_call_graph_octopus.gv",
                            format_fname=False):
        """Visualize the cfg call flow graph
        """
        nodes, edges = self.get_functions_call_edges()
        if format_fname:
            nodes_longname, edges = self.get_functions_call_edges(format_fname=True)

        g = Digraph(filename, filename=filename)
        g.attr(rankdir='LR')

        with g.subgraph(name='global') as c:

            export_list = [p[0] for p in self.analyzer.func_prototypes if p[3] == 'export']
            import_list = [p[0] for p in self.analyzer.func_prototypes if p[3] == 'import']
            call_indirect_list = enum_func_name_call_indirect(self.functions)

            try:
                indirect_target = [self.analyzer.func_prototypes[index][0] for index in self.analyzer.elements[0].get('elems')]
            except IndexError:
                indirect_target = []
            # create all the graph nodes (function name)
            for idx, node in enumerate(nodes):
                # name graph bubble
                node_name = node
                if format_fname:
                    node_name = nodes_longname[idx]

                # default style value
                fillcolor = "white"
                shape = "ellipse"
                style = "filled"

                if node in import_list:
                    logging.debug('import ' + node)
                    fillcolor = DESIGN_IMPORT.get('fillcolor')
                    shape = DESIGN_IMPORT.get('shape')
                    style = DESIGN_IMPORT.get('style')
                    c.node(node_name, fillcolor=fillcolor, shape=shape, style=style)
                elif node in export_list:
                    logging.debug('export ' + node)
                    fillcolor = DESIGN_EXPORT.get('fillcolor')
                    shape = DESIGN_EXPORT.get('shape')
                    style = DESIGN_EXPORT.get('style')
                    c.node(node_name, fillcolor=fillcolor, shape=shape, style=style)

                if node in indirect_target:
                    logging.debug('indirect_target ' + node)
                    shape = "hexagon"

                if node in call_indirect_list:
                    logging.debug('contain call_indirect ' + node)
                    style = "dashed"
                c.node(node_name, fillcolor=fillcolor, shape=shape, style=style)

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

    def visualize_instrs_per_funcs(self, show=True, save=True,
                                   out_filename="wasm_func_analytic.png",
                                   fontsize=8):
        """Visualize the instructions repartitions per functions
        """

        import numpy as np
        import matplotlib.pyplot as plt

        final = list()
        datas = list()

        # legend x axis - name functions
        group_names = tuple([func.name for func in self.functions])
        # number of functions
        ind = [x for x, _ in enumerate(self.functions)]

        # list all groups
        all_groups = [v for _, v in _groups.items()]

        # list()
        for func in self.functions:
            data = list()
            group = [i.group for i in func.instructions]
            for g in all_groups:
                data.append(group.count(g))
            datas.append(tuple(data))

        for idx in range(len(all_groups)):
            final.append(tuple([x[idx] for x in datas]))

        # choice color: https://matplotlib.org/users/colormaps.html
        color = iter(plt.cm.gist_rainbow(np.linspace(0, 1, len(all_groups))))
        stack = np.array([0 * len(all_groups)])
        for idx in range(len(all_groups)):
            if idx == 0:
                # first bar
                plt.barh(ind, final[idx], label=all_groups[idx],
                         align='center', color=next(color))
            else:
                plt.barh(ind, final[idx], label=all_groups[idx], left=stack,
                         align='center', color=next(color))

            stack = stack + np.array(final[idx])

        # Rotate x-labels on the x-axis
        plt.yticks(fontsize=fontsize)
        plt.ylim([0, len(self.functions)])
        plt.yticks(ind, group_names)
        plt.ylabel('Functions')
        plt.xlabel('Instructions count')
        plt.legend(loc="lower right")
        plt.title('Instructions count by function and group')

        # save
        if save:
            plt.savefig(out_filename)
        # show
        if show:
            plt.show()
