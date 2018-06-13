# extract from https://github.com/neo-project/neo-vm

pops = 0
pushes = 0

# fee doc - http://docs.neo.org/en-us/sc/systemfees.html
default = 0.001

_table = {
    # opcode:(mnemonic, immediate_operand_size, pops, pushes, gas, description)
    0x00: ('PUSH0', 0, 0, 1, 0, 'An empty array of bytes is pushed onto the stack.'),
    0x01: ('PUSHBYTES1', 0x01, 0, 0x01, 0, '0x01 byte will be push onto the stack'),
    0x02: ('PUSHBYTES2', 0x02, 0, 0x02, 0, '0x02 bytes will be push onto the stack'),
    0x03: ('PUSHBYTES3', 0x03, 0, 0x03, 0, '0x03 bytes will be push onto the stack'),
    0x04: ('PUSHBYTES4', 0x04, 0, 0x04, 0, '0x04 bytes will be push onto the stack'),
    0x05: ('PUSHBYTES5', 0x05, 0, 0x05, 0, '0x05 bytes will be push onto the stack'),
    0x06: ('PUSHBYTES6', 0x06, 0, 0x06, 0, '0x06 bytes will be push onto the stack'),
    0x07: ('PUSHBYTES7', 0x07, 0, 0x07, 0, '0x07 bytes will be push onto the stack'),
    0x08: ('PUSHBYTES8', 0x08, 0, 0x08, 0, '0x08 bytes will be push onto the stack'),
    0x09: ('PUSHBYTES9', 0x09, 0, 0x09, 0, '0x09 bytes will be push onto the stack'),
    0x0A: ('PUSHBYTES10', 0x0A, 0, 0x0A, 0, '0x0A bytes will be push onto the stack'),
    0x0B: ('PUSHBYTES11', 0x0B, 0, 0x0B, 0, '0x0B bytes will be push onto the stack'),
    0x0C: ('PUSHBYTES12', 0x0C, 0, 0x0C, 0, '0x0C bytes will be push onto the stack'),
    0x0D: ('PUSHBYTES13', 0x0D, 0, 0x0D, 0, '0x0D bytes will be push onto the stack'),
    0x0E: ('PUSHBYTES14', 0x0E, 0, 0x0E, 0, '0x0E bytes will be push onto the stack'),
    0x0F: ('PUSHBYTES15', 0x0F, 0, 0x0F, 0, '0x0F bytes will be push onto the stack'),
    0x10: ('PUSHBYTES16', 0x10, 0, 0x10, 0, '0x10 bytes will be push onto the stack'),
    0x11: ('PUSHBYTES17', 0x11, 0, 0x11, 0, '0x11 bytes will be push onto the stack'),
    0x12: ('PUSHBYTES18', 0x12, 0, 0x12, 0, '0x12 bytes will be push onto the stack'),
    0x13: ('PUSHBYTES19', 0x13, 0, 0x13, 0, '0x13 bytes will be push onto the stack'),
    0x14: ('PUSHBYTES20', 0x14, 0, 0x14, 0, '0x14 bytes will be push onto the stack'),
    0x15: ('PUSHBYTES21', 0x15, 0, 0x15, 0, '0x15 bytes will be push onto the stack'),
    0x16: ('PUSHBYTES22', 0x16, 0, 0x16, 0, '0x16 bytes will be push onto the stack'),
    0x17: ('PUSHBYTES23', 0x17, 0, 0x17, 0, '0x17 bytes will be push onto the stack'),
    0x18: ('PUSHBYTES24', 0x18, 0, 0x18, 0, '0x18 bytes will be push onto the stack'),
    0x19: ('PUSHBYTES25', 0x19, 0, 0x19, 0, '0x19 bytes will be push onto the stack'),
    0x1A: ('PUSHBYTES26', 0x1A, 0, 0x1A, 0, '0x1A bytes will be push onto the stack'),
    0x1B: ('PUSHBYTES27', 0x1B, 0, 0x1B, 0, '0x1B bytes will be push onto the stack'),
    0x1C: ('PUSHBYTES28', 0x1C, 0, 0x1C, 0, '0x1C bytes will be push onto the stack'),
    0x1D: ('PUSHBYTES29', 0x1D, 0, 0x1D, 0, '0x1D bytes will be push onto the stack'),
    0x1E: ('PUSHBYTES30', 0x1E, 0, 0x1E, 0, '0x1E bytes will be push onto the stack'),
    0x1F: ('PUSHBYTES31', 0x1F, 0, 0x1F, 0, '0x1F bytes will be push onto the stack'),
    0x20: ('PUSHBYTES32', 0x20, 0, 0x20, 0, '0x20 bytes will be push onto the stack'),
    0x21: ('PUSHBYTES33', 0x21, 0, 0x21, 0, '0x21 bytes will be push onto the stack'),
    0x22: ('PUSHBYTES34', 0x22, 0, 0x22, 0, '0x22 bytes will be push onto the stack'),
    0x23: ('PUSHBYTES35', 0x23, 0, 0x23, 0, '0x23 bytes will be push onto the stack'),
    0x24: ('PUSHBYTES36', 0x24, 0, 0x24, 0, '0x24 bytes will be push onto the stack'),
    0x25: ('PUSHBYTES37', 0x25, 0, 0x25, 0, '0x25 bytes will be push onto the stack'),
    0x26: ('PUSHBYTES38', 0x26, 0, 0x26, 0, '0x26 bytes will be push onto the stack'),
    0x27: ('PUSHBYTES39', 0x27, 0, 0x27, 0, '0x27 bytes will be push onto the stack'),
    0x28: ('PUSHBYTES40', 0x28, 0, 0x28, 0, '0x28 bytes will be push onto the stack'),
    0x29: ('PUSHBYTES41', 0x29, 0, 0x29, 0, '0x29 bytes will be push onto the stack'),
    0x2A: ('PUSHBYTES42', 0x2A, 0, 0x2A, 0, '0x2A bytes will be push onto the stack'),
    0x2B: ('PUSHBYTES43', 0x2B, 0, 0x2B, 0, '0x2B bytes will be push onto the stack'),
    0x2C: ('PUSHBYTES44', 0x2C, 0, 0x2C, 0, '0x2C bytes will be push onto the stack'),
    0x2D: ('PUSHBYTES45', 0x2D, 0, 0x2D, 0, '0x2D bytes will be push onto the stack'),
    0x2E: ('PUSHBYTES46', 0x2E, 0, 0x2E, 0, '0x2E bytes will be push onto the stack'),
    0x2F: ('PUSHBYTES47', 0x2F, 0, 0x2F, 0, '0x2F bytes will be push onto the stack'),
    0x30: ('PUSHBYTES48', 0x30, 0, 0x30, 0, '0x30 bytes will be push onto the stack'),
    0x31: ('PUSHBYTES49', 0x31, 0, 0x31, 0, '0x31 bytes will be push onto the stack'),
    0x32: ('PUSHBYTES50', 0x32, 0, 0x32, 0, '0x32 bytes will be push onto the stack'),
    0x33: ('PUSHBYTES51', 0x33, 0, 0x33, 0, '0x33 bytes will be push onto the stack'),
    0x34: ('PUSHBYTES52', 0x34, 0, 0x34, 0, '0x34 bytes will be push onto the stack'),
    0x35: ('PUSHBYTES53', 0x35, 0, 0x35, 0, '0x35 bytes will be push onto the stack'),
    0x36: ('PUSHBYTES54', 0x36, 0, 0x36, 0, '0x36 bytes will be push onto the stack'),
    0x37: ('PUSHBYTES55', 0x37, 0, 0x37, 0, '0x37 bytes will be push onto the stack'),
    0x38: ('PUSHBYTES56', 0x38, 0, 0x38, 0, '0x38 bytes will be push onto the stack'),
    0x39: ('PUSHBYTES57', 0x39, 0, 0x39, 0, '0x39 bytes will be push onto the stack'),
    0x3A: ('PUSHBYTES58', 0x3A, 0, 0x3A, 0, '0x3A bytes will be push onto the stack'),
    0x3B: ('PUSHBYTES59', 0x3B, 0, 0x3B, 0, '0x3B bytes will be push onto the stack'),
    0x3C: ('PUSHBYTES60', 0x3C, 0, 0x3C, 0, '0x3C bytes will be push onto the stack'),
    0x3D: ('PUSHBYTES61', 0x3D, 0, 0x3D, 0, '0x3D bytes will be push onto the stack'),
    0x3E: ('PUSHBYTES62', 0x3E, 0, 0x3E, 0, '0x3E bytes will be push onto the stack'),
    0x3F: ('PUSHBYTES63', 0x3F, 0, 0x3F, 0, '0x3F bytes will be push onto the stack'),
    0x40: ('PUSHBYTES64', 0x40, 0, 0x40, 0, '0x40 bytes will be push onto the stack'),
    0x41: ('PUSHBYTES65', 0x41, 0, 0x41, 0, '0x41 bytes will be push onto the stack'),
    0x42: ('PUSHBYTES66', 0x42, 0, 0x42, 0, '0x42 bytes will be push onto the stack'),
    0x43: ('PUSHBYTES67', 0x43, 0, 0x43, 0, '0x43 bytes will be push onto the stack'),
    0x44: ('PUSHBYTES68', 0x44, 0, 0x44, 0, '0x44 bytes will be push onto the stack'),
    0x45: ('PUSHBYTES69', 0x45, 0, 0x45, 0, '0x45 bytes will be push onto the stack'),
    0x46: ('PUSHBYTES70', 0x46, 0, 0x46, 0, '0x46 bytes will be push onto the stack'),
    0x47: ('PUSHBYTES71', 0x47, 0, 0x47, 0, '0x47 bytes will be push onto the stack'),
    0x48: ('PUSHBYTES72', 0x48, 0, 0x48, 0, '0x48 bytes will be push onto the stack'),
    0x49: ('PUSHBYTES73', 0x49, 0, 0x49, 0, '0x49 bytes will be push onto the stack'),
    0x4A: ('PUSHBYTES74', 0x4A, 0, 0x4A, 0, '0x4A bytes will be push onto the stack'),
    0x4B: ('PUSHBYTES75', 0x4B, 0, 0x4B, 0, '0x4B datas will be push onto the stack'),
    0x4C: ('PUSHDATA1', 1, 0, 1, 0, 'The next byte contains the number of bytes to be pushed onto the stack.'),
    0x4D: ('PUSHDATA2', 2, 0, 2, 0, 'The next two bytes contain the number of bytes to be pushed onto the stack.'),
    0x4E: ('PUSHDATA4', 4, 0, 4, 0, 'The next four bytes contain the number of bytes to be pushed onto the stack.'),
    0x4F: ('PUSHM1', 0, 0, 1, 0, 'The number -1 is pushed onto the stack.'),
    0x51: ('PUSH1', 0, 0, 1, 0, 'The number 1 is pushed onto the stack.'),
    0x52: ('PUSH2', 0, 0, 1, 0, 'The number 2 is pushed onto the stack.'),
    0x53: ('PUSH3', 0, 0, 1, 0, 'The number 3 is pushed onto the stack.'),
    0x54: ('PUSH4', 0, 0, 1, 0, 'The number 4 is pushed onto the stack.'),
    0x55: ('PUSH5', 0, 0, 1, 0, 'The number 5 is pushed onto the stack.'),
    0x56: ('PUSH6', 0, 0, 1, 0, 'The number 6 is pushed onto the stack.'),
    0x57: ('PUSH7', 0, 0, 1, 0, 'The number 7 is pushed onto the stack.'),
    0x58: ('PUSH8', 0, 0, 1, 0, 'The number 8 is pushed onto the stack.'),
    0x59: ('PUSH9', 0, 0, 1, 0, 'The number 9 is pushed onto the stack.'),
    0x5A: ('PUSH10', 0, 0, 1, 0, 'The number 10 is pushed onto the stack.'),
    0x5B: ('PUSH11', 0, 0, 1, 0, 'The number 11 is pushed onto the stack.'),
    0x5C: ('PUSH12', 0, 0, 1, 0, 'The number 12 is pushed onto the stack.'),
    0x5D: ('PUSH13', 0, 0, 1, 0, 'The number 13 is pushed onto the stack.'),
    0x5E: ('PUSH14', 0, 0, 1, 0, 'The number 14 is pushed onto the stack.'),
    0x5F: ('PUSH15', 0, 0, 1, 0, 'The number 15 is pushed onto the stack.'),
    0x60: ('PUSH16', 0, 0, 1, 0, 'The number 16 is pushed onto the stack.'),

    # Flow control
    0x61: ('NOP', 0, 0, 0, 0, 'Does nothing.'),
    0x62: ('JMP', 2, 0, 0, default, 'JUMP'),
    0x63: ('JMPIF', 2, 1, 0, default, 'CONDITIONNAL JUMP'),
    0x64: ('JMPIFNOT', 2, 1, 0, default, 'NEGATIVE CONDITIONNAL JUMP'),
    0x65: ('CALL', 2, 0, pushes, default, 'CALL FUNCTION'),
    0x66: ('RET', 0, 0, 0, default, 'RET FUNCTION'),
    0x67: ('APPCALL', 20, pops, pushes, 0.01, 'APPCALL'),
    0x68: ('SYSCALL', 1, pops, pushes, default, 'SYSCALL'),
    0x69: ('TAILCALL', 20, pops, pushes, 0.01, 'TAILCALL'),

    # Stack
    0x6A: ('DUPFROMALTSTACK', 0, 0, 1, default, ''),
    0x6B: ('TOALTSTACK', 0, 1, 1, default, 'Puts the input onto the top of the alt stack. Removes it from the main stack.'),
    0x6C: ('FROMALTSTACK', 0, 1, 1, default, 'Puts the input onto the top of the main stack. Removes it from the alt stack.'),
    0x6D: ('XDROP', 0, pops, pushes, default, ''),
    0x72: ('XSWAP', 0, 1, 0, default, ''),
    0x73: ('XTUCK', 0, 1, 1, default, ''),
    0x74: ('DEPTH', 0, 0, 1, default, 'Puts the number of stack items onto the stack.'),
    0x75: ('DROP', 0, 1, 0, default, 'Removes the top stack item.'),
    0x76: ('DUP', 0, 0, 1, default, 'Duplicates the top stack item.'),
    0x77: ('NIP', 0, 2, 1, default, 'Removes the second-to-top stack item.'),
    0x78: ('OVER', 0, 1, 2, default, 'Copies the second-to-top stack item to the top.'),
    0x79: ('PICK', 0, 1, 1, default, 'The item n back in the stack is copied to the top.'),
    0x7A: ('ROLL', 0, pops, pushes, default, 'The item n back in the stack is moved to the top.'),
    0x7B: ('ROT', 0, 3, 3, default, 'The top three items on the stack are rotated to the left.'),
    0x7C: ('SWAP', 0, 2, 2, default, 'The top two items on the stack are swapped.'),
    0x7D: ('TUCK', 0, 2, 3, default, 'The item at the top of the stack is copied and inserted before the second-to-top item.'),

    # Splice
    0x7E: ('CAT', 0, 2, 1, default, 'Concatenates two strings.'),
    0x7F: ('SUBSTR', 0, 3, 1, default, 'Returns a section of a string.'),
    0x80: ('LEFT', 0, 2, 1, default, 'Keeps only characters left of the specified point in a string.'),
    0x81: ('RIGHT', 0, 2, 1, default, 'Keeps only characters right of the specified point in a string.'),
    0x82: ('SIZE', 0, 1, 1, default, 'Returns the length of the input string.'),

    # Bitwise logic
    0x83: ('INVERT', 0, 1, 1, default, 'Flips all of the bits in the input.'),
    0x84: ('AND', 0, 2, 1, default, 'Boolean and between each bit in the inputs.'),
    0x85: ('OR', 0, 2, 1, default, 'Boolean or between each bit in the inputs.'),
    0x86: ('XOR', 0, 2, 1, default, 'Boolean exclusive or between each bit in the inputs.'),
    0x87: ('EQUAL', 0, 2, 1, default, 'Returns 1 if the inputs are exactly equal, 0 otherwise.'),
    0x88: ('OP_EQUALVERIFY', 0, pops, pushes, default, 'Same as OP_EQUAL, but runs OP_VERIFY afterward.'),
    0x89: ('OP_RESERVED1', 0, pops, pushes, default, 'Transaction is invalid unless occuring in an unexecuted OP_IF branch'),
    0x8A: ('OP_RESERVED2', 0, pops, pushes, default, 'Transaction is invalid unless occuring in an unexecuted OP_IF branch'),

    # Arithmetic
    # Note: Arithmetic inputs are limited to signed 32-bit integers, but may overflow their output.
    0x8B: ('INC', 0, 1, 1, default, '1 is added to the input.'),
    0x8C: ('DEC', 0, 1, 1, default, '1 is subtracted from the input.'),
    0x8D: ('SIGN', 0, 1, 1, default, ''),
    0x8F: ('NEGATE', 0, 1, 1, default, 'The sign of the input is flipped.'),
    0x90: ('ABS', 0, 1, 1, default, 'The input is made positive.'),
    0x91: ('NOT', 0, 1, 1, default, 'If the input is 0 or 1, it is flipped. Otherwise the output will be 0.'),
    0x92: ('NZ', 0, 1, 1, default, 'Returns 0 if the input is 0. 1 otherwise.'),
    0x93: ('ADD', 0, pops, pushes, default, 'a is added to b.'),
    0x94: ('SUB', 0, pops, pushes, default, 'b is subtracted from a.'),
    0x95: ('MUL', 0, pops, pushes, default, 'a is multiplied by b.'),
    0x96: ('DIV', 0, pops, pushes, default, 'a is divided by b.'),
    0x97: ('MOD', 0, pops, pushes, default, 'Returns the remainder after dividing a by b.'),
    0x98: ('SHL', 0, pops, pushes, default, 'Shifts a left b bits, preserving sign.'),
    0x99: ('SHR', 0, pops, pushes, default, 'Shifts a right b bits, preserving sign.'),
    0x9A: ('BOOLAND', 0, pops, pushes, default, 'If both a and b are not 0, the output is 1. Otherwise 0.'),
    0x9B: ('BOOLOR', 0, pops, pushes, default, 'If a or b is not 0, the output is 1. Otherwise 0.'),
    0x9C: ('NUMEQUAL', 0, pops, pushes, default, 'Returns 1 if the numbers are equal, 0 otherwise.'),
    0x9E: ('NUMNOTEQUAL', 0, pops, pushes, default, 'Returns 1 if the numbers are not equal, 0 otherwise.'),
    0x9F: ('LT', 0, pops, pushes, default, 'Returns 1 if a is less than b, 0 otherwise.'),
    0xA0: ('GT', 0, pops, pushes, default, 'Returns 1 if a is greater than b, 0 otherwise.'),
    0xA1: ('LTE', 0, pops, pushes, default, 'Returns 1 if a is less than or equal to b, 0 otherwise.'),
    0xA2: ('GTE', 0, pops, pushes, default, 'Returns 1 if a is greater than or equal to b, 0 otherwise.'),
    0xA3: ('MIN', 0, pops, pushes, default, 'Returns the smaller of a and b.'),
    0xA4: ('MAX', 0, pops, pushes, default, 'Returns the larger of a and b.'),
    0xA5: ('WITHIN', 0, pops, pushes, default, 'Returns 1 if x is within the specified range (left-inclusive), 0 otherwise.'),


    # Crypto
    #0xA6: ('RIPEMD160', 0, pops, pushes, default, 'The input is hashed using RIPEMD-160.'),
    0xA7: ('SHA1', 0, pops, pushes, 0.01, 'The input is hashed using SHA-1.'),
    0xA8: ('SHA256', 0, pops, pushes, 0.01, 'The input is hashed using SHA-256.'),
    0xA9: ('HASH160', 0, pops, pushes, 0.02, ''),
    0xAA: ('HASH256', 0, pops, pushes, 0.02, ''),
    0xAC: ('CHECKSIG', 0, pops, pushes, 0.1, ''),
    0xAD: ('VERIFY', 0, pops, pushes, 0.1, ''),
    0xAE: ('CHECKMULTISIG', 0, pops, pushes, 0.1, ''),


    # Array
    0xC0: ('ARRAYSIZE', 0, pops, pushes, default, ''),
    0xC1: ('PACK', 0, pops, pushes, default, ''),
    0xC2: ('UNPACK', 0, pops, pushes, default, ''),
    0xC3: ('PICKITEM', 0, pops, pushes, default, ''),
    0xC4: ('SETITEM', 0, pops, pushes, default, ''),
    0xC5: ('NEWARRAY', 0, pops, pushes, default, 'Used as reference type'),
    0xC6: ('NEWSTRUCT', 0, pops, pushes, default, 'Used as reference value '),
    0xC7: ('NEWMAP', 0, pops, pushes, default, ''),
    0xC8: ('APPEND', 0, pops, pushes, default, ''),
    0xC9: ('REVERSE', 0, pops, pushes, default, ''),
    0xCA: ('REMOVE', 0, pops, pushes, default, ''),
    0xCB: ('HASKEY', 0, pops, pushes, default, ''),
    0xCC: ('KEYS', 0, pops, pushes, default, ''),
    0xCD: ('VALUES', 0, pops, pushes, default, ''),

    # Exceptions
    0xF0: ('THROW', 0, 0, 0, default, ''),
    0xF1: ('THROWIFNOT', 0, 1, 0, default, '')
}


class Avm(object):
    """Bytecode for NEO VM."""

    def __init__(self):
        self.table = _table
        self.reverse_table = self._get_reverse_table()

    def _get_reverse_table(self):
        """Build an internal table used in the assembler."""
        reverse_table = {}
        for (opcode, (mnemonic, immediate_operand_size,
                      pops, pushes, gas, description)) in self.table.items():
            reverse_table[mnemonic] = opcode, mnemonic, immediate_operand_size, \
                pops, pushes, gas, description
        return reverse_table
