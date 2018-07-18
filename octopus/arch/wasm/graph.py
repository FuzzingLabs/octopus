from graphviz import Digraph
import logging

DESIGN_IMPORT = {'fillcolor': 'turquoise',
                 'shape': 'box',
                 'style': 'filled'}

DESIGN_EXPORT = {'fillcolor': 'grey',
                 'shape': 'box',
                 'style': 'filled'}

log = logging.getLogger(__name__)
log.setLevel(level=logging.WARNING)


class WasmCallGraph(object):
    def __init__(self, wasmcfg, filename="wasm_call_graph"):
        self.wasmcfg = wasmcfg
        self.filename = filename
        self.nodes, self.edges = wasmcfg.get_functions_call_edges(format_fname=False)

    def view(self, view=True):

        g = Digraph(self.filename, filename=self.filename,)
        g.attr(rankdir='LR')

        with g.subgraph(name='global') as c:

            export_list = [d['field_str'] for d in self.wasmcfg.analyzer.exports]
            import_list = [x for _, x, _ in self.wasmcfg.analyzer.imports_func]
            # create all the graph nodes (function name)
            for idx, node in enumerate(self.nodes):
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
            edges_counter = dict((x, self.edges.count(x)) for x in set(self.edges))
            # insert edges on the graph
            for edge, count in edges_counter.items():
                label = None
                if count > 1:
                    label = str(count)
                c.edge(edge.node_from, edge.node_to, label=label)

        g.render(self.filename, view=view)
