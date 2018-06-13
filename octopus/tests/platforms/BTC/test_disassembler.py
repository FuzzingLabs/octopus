from octopus.platforms.BTC.disassembler import BitcoinDisassembler
import unittest


class BtcDisassemblerTestCase(unittest.TestCase):

    def testDisassembleHex(self):
        def test(bytecode_hex, result):
            disasm = BitcoinDisassembler(bytecode_hex).disassemble(r_format='text')
            self.assertEqual(disasm, result)

        def testNumberInstructions(bytecode_hex, len_result):
            disasm = BitcoinDisassembler(bytecode_hex).disassemble()
            self.assertEqual(len(disasm), len_result)

        # good test case : https://ivy-lang.org/bitcoin

        # https://en.bitcoin.it/wiki/Transaction#Pay-to-PubkeyHash
        # classic scriptPubKey
        bytecode_hex = "76a9149ba386253ea698158b6d34802bb9b550f5ce36dd88ac"
        result = 'OP_DUP\nOP_HASH160\n9ba386253ea698158b6d34802bb9b550f5ce36dd\nOP_EQUALVERIFY\nOP_CHECKSIG'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 5)

        # LockWithMultisig
        bytecode_hex = "007b7b522102f3ce98f0f47f9b91156b15cc43dd0956dfb1b94f2cacd95856ee1473a8c0ad6a2103399e680b0dc1f53c0d4641ef5f4c1267b69125b5076e1230f6ff1f4a1c4286eb21021cc83c35ab6cf47f6aa473449218e49dfa6e33ec2f0eb9e4e1ff709848ebe66453ae"
        result = '0\nOP_ROT\nOP_ROT\n2\n02f3ce98f0f47f9b91156b15cc43dd0956dfb1b94f2cacd95856ee1473a8c0ad6a\n03399e680b0dc1f53c0d4641ef5f4c1267b69125b5076e1230f6ff1f4a1c4286eb\n021cc83c35ab6cf47f6aa473449218e49dfa6e33ec2f0eb9e4e1ff709848ebe664\n3\nOP_CHECKMULTISIG'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 9)

        # LockWithPublicKeyHash
        bytecode_hex = "76a82096b3fe1f4ec8fd076379267f72443bed81cc49c18a2913f7e1f0727f6f9f4fbf88ac"
        result = 'OP_DUP\nOP_SHA256\n96b3fe1f4ec8fd076379267f72443bed81cc49c18a2913f7e1f0727f6f9f4fbf\nOP_EQUALVERIFY\nOP_CHECKSIG'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 5)

        # RevealPreImage
        bytecode_hex = 'a820c0c89d16be9b625834782a90411ebb259040775ee921651979d15fed5da0c26987'
        result = 'OP_SHA256\nc0c89d16be9b625834782a90411ebb259040775ee921651979d15fed5da0c269\nOP_EQUAL'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 3)

        # RevealCollision
        bytecode_hex = '6e879169a77ca787'
        result = 'OP_2DUP\nOP_EQUAL\nOP_NOT\nOP_VERIFY\nOP_SHA1\nOP_SWAP\nOP_SHA1\nOP_EQUAL'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 8)

        # RevealFixedPoint
        bytecode_hex = '76a887'
        result = 'OP_DUP\nOP_SHA256\nOP_EQUAL'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 3)

        bytecode_hex = '00b17521020cd5ac6e63926130ebff8b7063fa2cc26f597d6babed4adac23bff79e2178cceac'
        result = '0\nOP_CHECKLOCKTIMEVERIFY\nOP_DROP\n020cd5ac6e63926130ebff8b7063fa2cc26f597d6babed4adac23bff79e2178cce\nOP_CHECKSIG'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 5)

        # LockDelay
        bytecode_hex = '210361256041a4496060fd78bc5a3584622166210a6aa190513393541a47ccf8a67bad012ab27551'
        result = '0361256041a4496060fd78bc5a3584622166210a6aa190513393541a47ccf8a67b\nOP_CHECKSIGVERIFY\n42\nOP_CHECKSEQUENCEVERIFY\nOP_DROP\n1'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 6)

        # TransferWithTimeout
        bytecode_hex = '2102e5707a829f684e9c9263872ecd30c0027ca1a558b22f08f2aafc33f7b2eabdc27c630145b17567ad2103edb42eb19ef3badb27a5f7d13843dd8a58de5c0f6b9d9f1ffbeca59e9d35b85b68ac'
        result = '02e5707a829f684e9c9263872ecd30c0027ca1a558b22f08f2aafc33f7b2eabdc2\nOP_SWAP\nOP_IF\n69\nOP_CHECKLOCKTIMEVERIFY\nOP_DROP\nOP_ELSE\nOP_CHECKSIGVERIFY\n03edb42eb19ef3badb27a5f7d13843dd8a58de5c0f6b9d9f1ffbeca59e9d35b85b\nOP_ENDIF\nOP_CHECKSIG'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 11)

        # EscrowWithDelay
        bytecode_hex = '2103d32df19c6a163f2c0b3f047756e9fc4765c41897f59d5029ea624d839d6391b27c63ad0350c300b27551670072522102930524687b853a7bb80b5f24748e4b926869d629eca69e6e2d7758417e3249b02102d4e2e6a73d19d7eb52df220a826db2b825282d3ac700d75222813094a7583afc567a53ae68'
        result = '03d32df19c6a163f2c0b3f047756e9fc4765c41897f59d5029ea624d839d6391b2\nOP_SWAP\nOP_IF\nOP_CHECKSIGVERIFY\n50000\nOP_CHECKSEQUENCEVERIFY\nOP_DROP\n1\nOP_ELSE\n0\nOP_2SWAP\n2\n02930524687b853a7bb80b5f24748e4b926869d629eca69e6e2d7758417e3249b0\n02d4e2e6a73d19d7eb52df220a826db2b825282d3ac700d75222813094a7583afc\n6\nOP_ROLL\n3\nOP_CHECKMULTISIG\nOP_ENDIF'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 19)

        bytecode_hex = '6a4c50010002ca6efb0fe92dfa51e3393db37e0f4b79bda0634256a0158264dc2da9c5eda6262340d1510b03723e77839290a59735eb9f1dbb167caf1803887b3b92bbe824d800000000000000000000000000'
        result = 'OP_RETURN\n010002ca6efb0fe92dfa51e3393db37e0f4b79bda0634256a0158264dc2da9c5eda6262340d1510b03723e77839290a59735eb9f1dbb167caf1803887b3b92bbe824d800000000000000000000000000'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 2)

        # decimal value display and not hex as usual
        bytecode_hex = '6a03666666'
        result = 'OP_RETURN\n6710886'
        test(bytecode_hex, result)
        testNumberInstructions(bytecode_hex, 2)

        # FAIL but don't now why
        '''
        txid = '0415e0adb2ebb67fc48e53825eb8b86b3e32a45d863adae97b15de6dc4255cba'
        bytecode_hex = '6a03e29891'
        result = 'OP_RETURN -7235358'
        result_expected = 'OP_RETURN -1153250'
        test(bytecode_hex, result_expected)
        testNumberInstructions(bytecode_hex, 2)

        txid = '853eebe9937654e19956753d6f4f8c6ae5e4744b2e391756ce02bc5e638e108d'
        bytecode_hex = '6a52534b424c4f434b3a5841945ab918147d4e33f7e90dbebb68dd7dd1c9da273ca082cd66721943b9ff'
        result = 'OP_RETURN 2 3 424c4f434b3a5841945ab918147d4e33f7e90dbebb68dd7dd1c9da273ca082cd66721943b9ff'
        result_expected = 'OP_RETURN 2 3 [error]'
        test(bytecode_hex, result_expected)
        testNumberInstructions(bytecode_hex, 4)
        '''


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BtcDisassemblerTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)