from graphviz import Digraph

from octopus.api.edge import (EDGE_UNCONDITIONAL,
                              EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
                              EDGE_FALLTHROUGH, EDGE_CALL)

import logging
log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)


def insert_edges_to_graph(graph, edges, call):
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
                 filename='graph.cfg.gv', design=None):
        self.basicblocks = basicblocks
        self.edges = edges
        self.filename = filename
        self.design = design or {'shape': 'box', 'fontname': 'Courier',
                                 'fontsize': '30.0'}

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
                    # the escape sequences "\n", "\l" and "\r" divide the label into lines,
                    # centered, left-justified, and right-justified, respectively.
                    label = label.replace('\n', '\l')
                    # create node
                    c.node(basicblock.name, label=label)

        # insert edges on the graph
        insert_edges_to_graph(g, self.edges, call)

        g.render(self.filename, view=view)
        # g.view()


class CFGGraph(Graph):

    def __init__(self, cfg, filename='graph.cfg.gv', design=None):
        Graph.__init__(self, cfg.basicblocks, cfg.edges, filename=filename,
                       design=design)
        self.cfg = cfg

    def view_functions_ssa(self, call=False, view=True):
        self.view_functions(view=view, call=call, ssa=True)

    def view_functions_simplify(self, call=False, view=True):
        self.view_functions(view=view, call=call, simplify=True)

    def view_functions(self, view=True, simplify=False, call=False, ssa=False, color='grey'):
        g = Digraph('G', filename=self.filename)

        count = 0
        for func in self.cfg.functions:
            with g.subgraph(name='cluster_%d' % count, node_attr=self.design) as c:
                if func.name == func.prefered_name:
                    name = func.name
                else:
                    name = func.prefered_name + ' - ' + func.name
                c.attr(label=name)
                c.attr(color=color)
                c.attr(fontsize='50.0')

                # create all the basicblocks (blocks)
                for basicblock in func.basicblocks:
                    if simplify:
                        # create node
                        c.node(basicblock.name, label=basicblock.name)
                    else:
                        if ssa:
                            label = basicblock.instructions_ssa()
                        else:
                            label = basicblock.instructions_details()
                        # the escape sequences "\n", "\l" and "\r" divide the label into lines,
                        # centered, left-justified, and right-justified, respectively.
                        label = label.replace('\n', '\l')
                        # create node
                        c.node(basicblock.name, label=label)

            count += 1

        # insert edges on the graph
        insert_edges_to_graph(g, self.cfg.edges, call)

        g.render(self.filename, view=view)
        # g.view()
