import unittest

from octopus.platforms.EOS.cfg import EosCFG
from octopus.analysis.graph import CallGraph


class EosCallGraphTestCase(unittest.TestCase):

    def testCallGraph(self):
        def callgraph(bytecode, result_nodes, length_edges, fname=False):
            cfg = EosCFG(bytecode)
            nodes, edges = cfg.get_functions_call_edges(fname)
            # visualize
            # graph = CallGraph(nodes, edges)
            # graph.view()
            self.assertEqual(nodes, result_nodes)
            self.assertEqual(len(edges), length_edges)

        # Helloworld
        bytecode_hex = "0061736d0100000001110460017f0060017e0060000060027e7e00021b0203656e76067072696e746e000103656e76067072696e7473000003030202030404017000000503010001071903066d656d6f7279020004696e69740002056170706c7900030a20020600411010010b17004120100120001000413010012001100041c00010010b0b3f050041040b04504000000041100b0d496e697420576f726c64210a000041200b0e48656c6c6f20576f726c643a20000041300b032d3e000041c0000b020a000029046e616d6504067072696e746e0100067072696e7473010004696e697400056170706c790201300131"
        r_nodes = ['printn(i64)', 'prints(i32)', 'init()', 'apply(i64 i64)']
        r_nodes2 = ['printn', 'prints', 'init', 'apply']
        len_edges = 6
        callgraph(bytecode_hex, r_nodes2, len_edges)
        callgraph(bytecode_hex, r_nodes, len_edges, fname=True)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(EosCallGraphTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
