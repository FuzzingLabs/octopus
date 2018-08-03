import unittest

from octopus.arch.wasm.cfg import WasmCFG

EXAMPLE_PATH = "examples/wasm/samples/"


class WasmCFGraphTestCase(unittest.TestCase):

    def testCallGraph(self):
        def callgraph(bytecode, result_nodes, length_edges):
            cfg = WasmCFG(bytecode)
            nodes, edges = cfg.get_functions_call_edges()
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

        # Helloworld
        module_bytecode = read_file(EXAMPLE_PATH + "helloworld.wasm")
        r_nodes = ['print(i32)', 'main()']
        callgraph(module_bytecode, r_nodes, 1)
        controlflowgraph(module_bytecode, 1, 1, 0)

        # fibonacci
        module_bytecode = read_file(EXAMPLE_PATH + "fib.wasm")
        r_nodes = ['i32 fib(i32)']
        len_call_edges = 2
        callgraph(module_bytecode, r_nodes, len_call_edges)
        controlflowgraph(module_bytecode, 1, 3, 2)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(WasmCFGraphTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
