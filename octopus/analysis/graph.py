from graphviz import Digraph

from octopus.core.edge \
    import (EDGE_UNCONDITIONAL,
            EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
            EDGE_FALLTHROUGH, EDGE_CALL)


def insert_edges_to_graph(graph, edges, call=False):
    # remove duplicate edges
    edges = list(set(edges))

    # create link between block
    for edge in edges:

        if edge.type == EDGE_UNCONDITIONAL:
            graph.edge(edge.node_from, edge.node_to, color='blue')
        elif edge.type == EDGE_CONDITIONAL_TRUE:
            graph.edge(edge.node_from, edge.node_to, color='green')
        elif edge.type == EDGE_CONDITIONAL_FALSE:
            graph.edge(edge.node_from, edge.node_to, color='red')
        elif edge.type == EDGE_FALLTHROUGH:
            graph.edge(edge.node_from, edge.node_to, color='cyan')
        elif edge.type == EDGE_CALL and call:
            graph.edge(edge.node_from, edge.node_to, color='yellow')
        else:
            raise Exception('Edge type unknown')


class Graph(object):

    def __init__(self, basicblocks, edges, functions=None,
                 filename='graph.gv', design=None):
        self.basicblocks = basicblocks
        self.edges = edges
        self.filename = filename
        self.design = design or {'shape': 'box', 'fontname': 'Courier',
                                 'fontsize': '30.0', 'rank': 'same'}

    def view_ssa(self, call=False, view=True):
        self.view(view=view, call=call, ssa=True)

    def view_simplify(self, call=False, view=True):
        self.view(view=view, call=call, simplify=True)

    def view(self, view=True, simplify=False, call=False, ssa=False):
        g = Digraph(self.filename, filename=self.filename)

        with g.subgraph(name='global', node_attr=self.design) as c:
            c.label = 'global'

            # create all the basicblocks (blocks)
            for basicblock in self.basicblocks:
                if simplify:
                    # create node
                    c.node(basicblock.name, label=basicblock.name)
                else:
                    if ssa:
                        label = basicblock.instructions_ssa()
                    else:
                        label = basicblock.instructions_details()
                    # the escape sequences "\n", "\l" and "\r"
                    # divide the label into lines, centered,
                    # left-justified, and right-justified, respectively.
                    label = label.replace('\n', '\l')
                    # create node
                    c.node(basicblock.name, label=label)

        # insert edges on the graph
        insert_edges_to_graph(g, self.edges, call)

        g.render(self.filename, view=view)
        # g.view()


class CallGraph(object):
    def __init__(self, nodes, edges,
                 filename='call_graph.gv', design=None):
        self.nodes = nodes
        self.edges = edges
        self.filename = filename
        self.design = design or {'shape': 'box'}

    def view(self, view=True):
        g = Digraph(self.filename, filename=self.filename,
                    graph_attr=self.design)
        g.attr(rankdir='LR')

        with g.subgraph(name='global', node_attr=self.design) as c:

            # create all the graph nodes (function name)
            for idx, node in enumerate(self.nodes):
                # print('%d %s' % (idx, node))
                c.node(node)

            # check if multiple same edges
            # in that case, put the number into label
            edges_counter = dict((x,self.edges.count(x)) for x in set(self.edges))
            # insert edges on the graph
            for edge, count in edges_counter.items():
                label = None
                if count > 1:
                    label = str(count)
                c.edge(edge.node_from, edge.node_to, label=label, color='black')

        g.render(self.filename, view=view)


class CFGGraph(Graph):

    def __init__(self, cfg, filename='graph.cfg.gv', design=None):
        Graph.__init__(self, cfg.basicblocks, cfg.edges, filename=filename,
                       design=design)
        self.cfg = cfg

    def view_functions_ssa(self, call=False, view=True):
        self.view_functions(view=view, call=call, ssa=True)

    def view_functions_simplify(self, call=False, view=True):
        self.view_functions(view=view, call=call, simplify=True)

    def view_functions(self, only_func_name=None, view=True, simplify=False, call=False, ssa=False, color='grey'):
        g = Digraph('G', filename=self.filename)
        g.attr(rankdir='TB')
        g.attr(overlap='scale')
        g.attr(splines='polyline')
        g.attr(ratio='fill')

        functions = self.cfg.functions
        # only show functions listed
        if only_func_name:
            functions = [func for func in self.cfg.functions if func.name in only_func_name]

        for idx, func in enumerate(functions):
            with g.subgraph(name='cluster_%d' % idx, node_attr=self.design) as c:
                if func.name == func.prefered_name:
                    name = func.name
                else:
                    name = func.prefered_name + ' - ' + func.name
                c.attr(label=name)
                c.attr(color=color)
                c.attr(fontsize='50.0')
                c.attr(overlap='false')
                c.attr(splines='polyline')
                c.attr(ratio='fill')

                # create all the basicblocks (blocks)
                for basicblock in func.basicblocks:
                    if simplify:
                        # create node
                        c.node(basicblock.name, label=basicblock.name, splines='true')
                    else:
                        if ssa:
                            label = basicblock.instructions_ssa()
                        else:
                            label = basicblock.instructions_details()
                        # the escape sequences "\n", "\l" and "\r"
                        # divide the label into lines, centered,
                        # left-justified, and right-justified, respectively.
                        label = label.replace('\n', '\l')
                        # create node
                        c.node(basicblock.name, label=label)

        edges = self.cfg.edges
        # only get corresponding edges
        if only_func_name:
            functions_block = [func.basicblocks for func in functions]
            block_name = [b.name for block_l in functions_block for b in block_l]
            edges = [edge for edge in edges if (edge.node_from in block_name or edge.node_to in block_name)]
        # insert edges on the graph
        insert_edges_to_graph(g, edges, call)

        g.render(self.filename, view=view)
        # g.view()
