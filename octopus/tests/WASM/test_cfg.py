import unittest
import os

from octopus.arch.wasm.cfg import WasmCFG

EXAMPLE_PATH = "/../../../examples/wasm/samples/"


class WasmCFGraphTestCase(unittest.TestCase):

    def testCallGraph(self):
        def callgraph(bytecode, result_nodes, length_edges, fname=False):
            cfg = WasmCFG(bytecode)
            nodes, edges = cfg.get_functions_call_edges(fname)
            # visualize
            # cfg.visualize_call_flow()
            self.assertEqual(nodes, result_nodes)
            self.assertEqual(len(edges), length_edges)

        def controlflowgraph(bytecode, len_func, len_blocks, len_edges):
            cfg = WasmCFG(bytecode)
            functions = cfg.functions
            basicblocks = cfg.basicblocks
            edges = cfg.edges
            # visualize
            # cfg.visualize_call_flow()
            self.assertEqual(len(functions), len_func)
            self.assertEqual(len(basicblocks), len_blocks)
            self.assertEqual(len(edges), len_edges)

        def read_file(file_name):
            with open(file_name, 'rb') as f:
                module_bytecode = f.read()
            return module_bytecode

        path = os.path.dirname(os.path.realpath(__file__)) + EXAMPLE_PATH
        # Helloworld
        module_bytecode = read_file(path + "helloworld.wasm")
        r_nodes = ['print(i32)', 'main()']
        r_nodes2 = ['print', 'main']
        callgraph(module_bytecode, r_nodes, 1, fname=True)
        callgraph(module_bytecode, r_nodes2, 1, fname=False)
        controlflowgraph(module_bytecode, 1, 1, 0)

        # fibonacci
        module_bytecode = read_file(path + "fib.wasm")
        r_nodes = ['i32 fib(i32)']
        r_nodes2 = ['fib']
        len_call_edges = 2
        callgraph(module_bytecode, r_nodes, len_call_edges, fname=True)
        callgraph(module_bytecode, r_nodes2, len_call_edges, fname=False)
        controlflowgraph(module_bytecode, 1, 3, 2)

        # fibonacci 2 with if-else
        module_bytecode = read_file(path + "fibc.wasm")
        r_nodes = ['i32 _fib(i32)', 'runPostSets()', '__post_instantiate()']
        r_nodes2 = ['_fib', 'runPostSets', '__post_instantiate']
        len_call_edges = 2
        callgraph(module_bytecode, r_nodes, len_call_edges, fname=True)
        callgraph(module_bytecode, r_nodes2, len_call_edges, fname=False)
        controlflowgraph(module_bytecode, 3, 10, 9)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(WasmCFGraphTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
