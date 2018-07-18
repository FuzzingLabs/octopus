import unittest

from octopus.platforms.NEO.disassembler import NeoDisassembler


class NeoDisassemblerTestCase(unittest.TestCase):

    def testDisassemble(self):

        def disassemble(bytecode_hex, result):
            disasm = len(NeoDisassembler(bytecode_hex).disassemble())
            self.assertEqual(disasm, result)

        def disasmOne(bytecode, result):
            disasm = str(NeoDisassembler(bytecode).disassemble_opcode(bytecode))
            self.assertEqual(disasm, result)

        def disasm(bytecode, result):
            disasm = NeoDisassembler(bytecode_hex).disassemble(r_format='text')
            self.assertEqual(disasm, result)

        bytecode = b'Q\xc5kaah\x16Neo.Storage.GetContext\x06secret\x0bHello WorldaRrh\x0fNeo.Storage.Putaah\x16Neo.Storage.GetContext\x06secreta|h\x0fNeo.Storage.Getlvk\x00Rz\xc4b\x03\x00lvk\x00\xc3aluf'
        bytecode_hex = "0x51c56b616168164e656f2e53746f726167652e476574436f6e74657874067365637265740b48656c6c6f20576f726c64615272680f4e656f2e53746f726167652e507574616168164e656f2e53746f726167652e476574436f6e7465787406736563726574617c680f4e656f2e53746f726167652e4765746c766b00527ac46203006c766b00c3616c7566"
        result = 'PUSH1\nNEWARRAY\nTOALTSTACK\nNOP\nNOP\nSYSCALL 0x4e656f2e53746f726167652e476574436f6e74657874\nPUSHBYTES6 0x736563726574\nPUSHBYTES11 0x48656c6c6f20576f726c64\nNOP\nPUSH2\nXSWAP\nSYSCALL 0x4e656f2e53746f726167652e507574\nNOP\nNOP\nSYSCALL 0x4e656f2e53746f726167652e476574436f6e74657874\nPUSHBYTES6 0x736563726574\nNOP\nSWAP\nSYSCALL 0x4e656f2e53746f726167652e476574\nFROMALTSTACK\nDUP\nTOALTSTACK\nPUSH0\nPUSH2\nROLL\nSETITEM\nJMP 0x300\nFROMALTSTACK\nDUP\nTOALTSTACK\nPUSH0\nPICKITEM\nNOP\nFROMALTSTACK\nDROP\nRET'

        bytecode_one_instr = b'h\x16Neo.Storage.GetContext'
        result_one_instr = 'SYSCALL 0x4e656f2e53746f726167652e476574436f6e74657874'

        disasmOne(bytecode_one_instr, result_one_instr)
        disasm(bytecode, result)
        disassemble(bytecode_hex, 36)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(NeoDisassembler)
    unittest.TextTestRunner(verbosity=2).run(suite)
