# based on https://en.bitcoin.it/wiki/Script

pops = 0
pushes = 0
gas = 0

_table = {
    # opcode:(mnemonic, immediate_operand_size, pops, pushes, gas, description)
    # Constants
    0x00: ('OP_FALSE', 0, 0, 1, gas, 'An empty array of bytes is pushed onto the stack.'),
    0x00: ('OP_0', 0, 0, 1, gas, 'An empty array of bytes is pushed onto the stack.'),
    0x01: ('', 0x01, 0, 0x01, gas, '0x01 byte will be push onto the stack'),
    0x02: ('', 0x02, 0, 0x02, gas, '0x02 bytes will be push onto the stack'),
    0x03: ('', 0x03, 0, 0x03, gas, '0x03 bytes will be push onto the stack'),
    0x04: ('', 0x04, 0, 0x04, gas, '0x04 bytes will be push onto the stack'),
    0x05: ('', 0x05, 0, 0x05, gas, '0x05 bytes will be push onto the stack'),
    0x06: ('', 0x06, 0, 0x06, gas, '0x06 bytes will be push onto the stack'),
    0x07: ('', 0x07, 0, 0x07, gas, '0x07 bytes will be push onto the stack'),
    0x08: ('', 0x08, 0, 0x08, gas, '0x08 bytes will be push onto the stack'),
    0x09: ('', 0x09, 0, 0x09, gas, '0x09 bytes will be push onto the stack'),
    0x0A: ('', 0x0A, 0, 0x0A, gas, '0x0A bytes will be push onto the stack'),
    0x0B: ('', 0x0B, 0, 0x0B, gas, '0x0B bytes will be push onto the stack'),
    0x0C: ('', 0x0C, 0, 0x0C, gas, '0x0C bytes will be push onto the stack'),
    0x0D: ('', 0x0D, 0, 0x0D, gas, '0x0D bytes will be push onto the stack'),
    0x0E: ('', 0x0E, 0, 0x0E, gas, '0x0E bytes will be push onto the stack'),
    0x0F: ('', 0x0F, 0, 0x0F, gas, '0x0F bytes will be push onto the stack'),
    0x10: ('', 0x10, 0, 0x10, gas, '0x10 bytes will be push onto the stack'),
    0x11: ('', 0x11, 0, 0x11, gas, '0x11 bytes will be push onto the stack'),
    0x12: ('', 0x12, 0, 0x12, gas, '0x12 bytes will be push onto the stack'),
    0x13: ('', 0x13, 0, 0x13, gas, '0x13 bytes will be push onto the stack'),
    0x14: ('', 0x14, 0, 0x14, gas, '0x14 bytes will be push onto the stack'),
    0x15: ('', 0x15, 0, 0x15, gas, '0x15 bytes will be push onto the stack'),
    0x16: ('', 0x16, 0, 0x16, gas, '0x16 bytes will be push onto the stack'),
    0x17: ('', 0x17, 0, 0x17, gas, '0x17 bytes will be push onto the stack'),
    0x18: ('', 0x18, 0, 0x18, gas, '0x18 bytes will be push onto the stack'),
    0x19: ('', 0x19, 0, 0x19, gas, '0x19 bytes will be push onto the stack'),
    0x1A: ('', 0x1A, 0, 0x1A, gas, '0x1A bytes will be push onto the stack'),
    0x1B: ('', 0x1B, 0, 0x1B, gas, '0x1B bytes will be push onto the stack'),
    0x1C: ('', 0x1C, 0, 0x1C, gas, '0x1C bytes will be push onto the stack'),
    0x1D: ('', 0x1D, 0, 0x1D, gas, '0x1D bytes will be push onto the stack'),
    0x1E: ('', 0x1E, 0, 0x1E, gas, '0x1E bytes will be push onto the stack'),
    0x1F: ('', 0x1F, 0, 0x1F, gas, '0x1F bytes will be push onto the stack'),
    0x20: ('', 0x20, 0, 0x20, gas, '0x20 bytes will be push onto the stack'),
    0x21: ('', 0x21, 0, 0x21, gas, '0x21 bytes will be push onto the stack'),
    0x22: ('', 0x22, 0, 0x22, gas, '0x22 bytes will be push onto the stack'),
    0x23: ('', 0x23, 0, 0x23, gas, '0x23 bytes will be push onto the stack'),
    0x24: ('', 0x24, 0, 0x24, gas, '0x24 bytes will be push onto the stack'),
    0x25: ('', 0x25, 0, 0x25, gas, '0x25 bytes will be push onto the stack'),
    0x26: ('', 0x26, 0, 0x26, gas, '0x26 bytes will be push onto the stack'),
    0x27: ('', 0x27, 0, 0x27, gas, '0x27 bytes will be push onto the stack'),
    0x28: ('', 0x28, 0, 0x28, gas, '0x28 bytes will be push onto the stack'),
    0x29: ('', 0x29, 0, 0x29, gas, '0x29 bytes will be push onto the stack'),
    0x2A: ('', 0x2A, 0, 0x2A, gas, '0x2A bytes will be push onto the stack'),
    0x2B: ('', 0x2B, 0, 0x2B, gas, '0x2B bytes will be push onto the stack'),
    0x2C: ('', 0x2C, 0, 0x2C, gas, '0x2C bytes will be push onto the stack'),
    0x2D: ('', 0x2D, 0, 0x2D, gas, '0x2D bytes will be push onto the stack'),
    0x2E: ('', 0x2E, 0, 0x2E, gas, '0x2E bytes will be push onto the stack'),
    0x2F: ('', 0x2F, 0, 0x2F, gas, '0x2F bytes will be push onto the stack'),
    0x30: ('', 0x30, 0, 0x30, gas, '0x30 bytes will be push onto the stack'),
    0x31: ('', 0x31, 0, 0x31, gas, '0x31 bytes will be push onto the stack'),
    0x32: ('', 0x32, 0, 0x32, gas, '0x32 bytes will be push onto the stack'),
    0x33: ('', 0x33, 0, 0x33, gas, '0x33 bytes will be push onto the stack'),
    0x34: ('', 0x34, 0, 0x34, gas, '0x34 bytes will be push onto the stack'),
    0x35: ('', 0x35, 0, 0x35, gas, '0x35 bytes will be push onto the stack'),
    0x36: ('', 0x36, 0, 0x36, gas, '0x36 bytes will be push onto the stack'),
    0x37: ('', 0x37, 0, 0x37, gas, '0x37 bytes will be push onto the stack'),
    0x38: ('', 0x38, 0, 0x38, gas, '0x38 bytes will be push onto the stack'),
    0x39: ('', 0x39, 0, 0x39, gas, '0x39 bytes will be push onto the stack'),
    0x3A: ('', 0x3A, 0, 0x3A, gas, '0x3A bytes will be push onto the stack'),
    0x3B: ('', 0x3B, 0, 0x3B, gas, '0x3B bytes will be push onto the stack'),
    0x3C: ('', 0x3C, 0, 0x3C, gas, '0x3C bytes will be push onto the stack'),
    0x3D: ('', 0x3D, 0, 0x3D, gas, '0x3D bytes will be push onto the stack'),
    0x3E: ('', 0x3E, 0, 0x3E, gas, '0x3E bytes will be push onto the stack'),
    0x3F: ('', 0x3F, 0, 0x3F, gas, '0x3F bytes will be push onto the stack'),
    0x40: ('', 0x40, 0, 0x40, gas, '0x40 bytes will be push onto the stack'),
    0x41: ('', 0x41, 0, 0x41, gas, '0x41 bytes will be push onto the stack'),
    0x42: ('', 0x42, 0, 0x42, gas, '0x42 bytes will be push onto the stack'),
    0x43: ('', 0x43, 0, 0x43, gas, '0x43 bytes will be push onto the stack'),
    0x44: ('', 0x44, 0, 0x44, gas, '0x44 bytes will be push onto the stack'),
    0x45: ('', 0x45, 0, 0x45, gas, '0x45 bytes will be push onto the stack'),
    0x46: ('', 0x46, 0, 0x46, gas, '0x46 bytes will be push onto the stack'),
    0x47: ('', 0x47, 0, 0x47, gas, '0x47 bytes will be push onto the stack'),
    0x48: ('', 0x48, 0, 0x48, gas, '0x48 bytes will be push onto the stack'),
    0x49: ('', 0x49, 0, 0x49, gas, '0x49 bytes will be push onto the stack'),
    0x4A: ('', 0x4A, 0, 0x4A, gas, '0x4A bytes will be push onto the stack'),
    0x4B: ('', 0x4B, 0, 0x4B, gas, '0x4B datas will be push onto the stack'),
    0x4C: ('OP_PUSHDATA1', 1, 0, 1, gas, 'The next byte contains the number of bytes to be pushed onto the stack.'),
    0x4D: ('OP_PUSHDATA2', 2, 0, 2, gas, 'The next two bytes contain the number of bytes to be pushed onto the stack.'),
    0x4E: ('OP_PUSHDATA4', 4, 0, 4, gas, 'The next four bytes contain the number of bytes to be pushed onto the stack.'),
    0x4F: ('OP_1NEGATE', 0, 0, 1, gas, 'The number -1 is pushed onto the stack.'),
    0x51: ('OP_TRUE', 0, 0, 1, gas, 'The number 1 is pushed onto the stack.'),
    0x51: ('OP_1', 0, 0, 1, gas, 'The number 1 is pushed onto the stack.'),
    0x52: ('OP_2', 0, 0, 1, gas, 'The number 2 is pushed onto the stack.'),
    0x53: ('OP_3', 0, 0, 1, gas, 'The number 3 is pushed onto the stack.'),
    0x54: ('OP_4', 0, 0, 1, gas, 'The number 4 is pushed onto the stack.'),
    0x55: ('OP_5', 0, 0, 1, gas, 'The number 5 is pushed onto the stack.'),
    0x56: ('OP_6', 0, 0, 1, gas, 'The number 6 is pushed onto the stack.'),
    0x57: ('OP_7', 0, 0, 1, gas, 'The number 7 is pushed onto the stack.'),
    0x58: ('OP_8', 0, 0, 1, gas, 'The number 8 is pushed onto the stack.'),
    0x59: ('OP_9', 0, 0, 1, gas, 'The number 9 is pushed onto the stack.'),
    0x5A: ('OP_10', 0, 0, 1, gas, 'The number 10 is pushed onto the stack.'),
    0x5B: ('OP_11', 0, 0, 1, gas, 'The number 11 is pushed onto the stack.'),
    0x5C: ('OP_12', 0, 0, 1, gas, 'The number 12 is pushed onto the stack.'),
    0x5D: ('OP_13', 0, 0, 1, gas, 'The number 13 is pushed onto the stack.'),
    0x5E: ('OP_14', 0, 0, 1, gas, 'The number 14 is pushed onto the stack.'),
    0x5F: ('OP_15', 0, 0, 1, gas, 'The number 15 is pushed onto the stack.'),
    0x60: ('OP_16', 0, 0, 1, gas, 'The number 16 is pushed onto the stack.'),

    # Flow control
    0x61: ('OP_NOP', 0, 0, 0, gas, 'Does nothing.'),
    0x63: ('OP_IF', 0, 1, 0, gas, 'If the top stack value is not False, the statements are executed. The top stack value is removed.'),
    0x64: ('OP_NOTIF', 0, 1, 0, gas, 'If the top stack value is False, the statements are executed. The top stack value is removed.'),
    0x67: ('OP_ELSE', 0, pops, pushes, gas, 'If the preceding OP_IF or OP_NOTIF or OP_ELSE was not executed then these statements are and if the preceding OP_IF or OP_NOTIF or OP_ELSE was executed then these statements are not.'),
    0x68: ('OP_ENDIF', 0, pops, pushes, gas, 'Ends an if/else block. All blocks must end, or the transaction is invalid. An OP_ENDIF without OP_IF earlier is also invalid.'),
    0x69: ('OP_VERIFY', 0, 0, 0, gas, 'Marks transaction as invalid if top stack value is not true. The top stack value is removed.'),
    0x6A: ('OP_RETURN', 0, 0, 1, gas, 'Marks transaction as invalid. A standard way of attaching extra data to transactions is to add a zero-value output with a scriptPubKey consisting of OP_RETURN followed by exactly one pushdata op. Such outputs are provably unspendable, reducing their cost to the network. Currently it is usually considered non-standard (though valid) for a transaction to have more than one OP_RETURN output or an OP_RETURN output with more than one pushdata op.'),

    # Stack
    0x6B: ('OP_TOALTSTACK', 0, 1, 1, gas, 'Puts the input onto the top of the alt stack. Removes it from the main stack.'),
    0x6C: ('OP_FROMALTSTACK', 0, 1, 1, gas, 'Puts the input onto the top of the main stack. Removes it from the alt stack.'),
    0x73: ('OP_IFDUP', 0, 0, 1, gas, 'If the top stack value is not 0, duplicate it.'),
    0x74: ('OP_DEPTH', 0, 0, 1, gas, 'Puts the number of stack items onto the stack.'),
    0x75: ('OP_DROP', 0, 1, 0, gas, 'Removes the top stack item.'),
    0x76: ('OP_DUP', 0, 0, 1, gas, 'Duplicates the top stack item.'),
    0x77: ('OP_NIP', 0, 1, 0, gas, 'Removes the second-to-top stack item.'),
    0x78: ('OP_OVER', 0, 0, 1, gas, 'Copies the second-to-top stack item to the top.'),
    0x79: ('OP_PICK', 0, 0, 1, gas, 'The item n back in the stack is copied to the top.'),
    0x7A: ('OP_ROLL', 0, 0, 0, gas, 'The item n back in the stack is moved to the top.'),
    0x7B: ('OP_ROT', 0, 3, 3, gas, 'The top three items on the stack are rotated to the left.'),
    0x7C: ('OP_SWAP', 0, 2, 2, gas, 'The top two items on the stack are swapped.'),
    0x7D: ('OP_TUCK', 0, 2, 3, gas, 'The item at the top of the stack is copied and inserted before the second-to-top item.'),
    0x6D: ('OP_2DROP', 0, 2, 0, gas, 'Removes the top two stack items.'),
    0x6E: ('OP_2DUP', 0, 2, 4, gas, 'Duplicates the top two stack items.'),
    0x6F: ('OP_3DUP', 0, 3, 6, gas, 'Duplicates the top three stack items.'),
    0x70: ('OP_2OVER', 0, 4, 6, gas, 'Copies the pair of items two spaces back in the stack to the front.'),
    0x71: ('OP_2ROT', 0, 6, 6, gas, 'The fifth and sixth items back are moved to the top of the stack.'),
    0x72: ('OP_2SWAP', 0, 4, 4, gas, 'Swaps the top two pairs of items.'),

    # Splice
    0x7E: ('OP_CAT', 0, 0, 0, gas, 'Concatenates two strings. DISABLED.'),
    0x7F: ('OP_SUBSTR', 0, 0, 0, gas, 'Returns a section of a string. DISABLED.'),
    0x80: ('OP_LEFT', 0, 0, 0, gas, 'Keeps only characters left of the specified point in a string. DISABLED.'),
    0x81: ('OP_RIGHT', 0, 0, 0, gas, 'Keeps only characters right of the specified point in a string. DISABLED.'),
    0x82: ('OP_SIZE', 0, 1, 2, gas, 'Pushes the string length of the top element of the stack (without popping it).'),

    # Bitwise logic
    0x83: ('OP_INVERT', 0, pops, pushes, gas, 'Flips all of the bits in the input. DISABLED.'),
    0x84: ('OP_AND', 0, pops, pushes, gas, 'Boolean and between each bit in the inputs. DISABLED.'),
    0x85: ('OP_OR', 0, pops, pushes, gas, 'Boolean or between each bit in the inputs. DISABLED.'),
    0x86: ('OP_XOR', 0, pops, pushes, gas, 'Boolean exclusive or between each bit in the inputs. DISABLED.'),
    0x87: ('OP_EQUAL', 0, 2, 3, gas, 'Returns 1 if the inputs are exactly equal, 0 otherwise.'),
    0x88: ('OP_EQUALVERIFY', 0, 2, 2, gas, 'Same as OP_EQUAL, but runs OP_VERIFY afterward.'),

    # Arithmetic
    # Note: Arithmetic inputs are limited to signed 32-bit integers, but may overflow their output.
    # If any input value for any of these commands is longer than 4 bytes, the script must abort and fail. If any opcode marked as disabled is present in a script - it must also abort and fail.
    0x8B: ('OP_1ADD', 0, 0, 0, gas, '1 is added to the input.'),
    0x8C: ('OP_1SUB', 0, 0, 0, gas, '1 is subtracted from the input.'),
    0x8D: ('OP_2MUL', 0, 0, 0, gas, 'The input is multiplied by 2. DISABLED.'),
    0x8E: ('OP_2DIV', 0, 0, 0, gas, 'The input is divided by 2. DISABLED.'),
    0x8F: ('OP_NEGATE', 0, 0, 0, gas, 'The sign of the input is flipped.'),
    0x90: ('OP_ABS', 0, 0, 0, gas, 'The input is made positive.'),
    0x91: ('OP_NOT', 0, 0, 0, gas, 'If the input is 0 or 1, it is flipped. Otherwise the output will be 0.'),
    0x92: ('OP_0NOTEQUAL', 0, pops, pushes, gas, 'Returns 0 if the input is 0. 1 otherwise.'),
    0x93: ('OP_ADD', 0, 0, 0, gas, 'a is added to b.'),
    0x94: ('OP_SUB', 0, 0, 0, gas, 'b is subtracted from a.'),
    0x95: ('OP_MUL', 0, 0, 0, gas, 'a is multiplied by b.'),
    0x96: ('OP_DIV', 0, 0, 0, gas, 'a is divided by b. DISABLED.'),
    0x97: ('OP_MOD', 0, 0, 0, gas, 'Returns the remainder after dividing a by b. DISABLED.'),
    0x98: ('OP_LSHIFT', 0, 0, 0, gas, 'Shifts a left b bits, preserving sign. DISABLED.'),
    0x99: ('OP_RSHIFT', 0, 0, 0, gas, 'Shifts a right b bits, preserving sign.DISABLED.'),
    0x9A: ('OP_BOOLAND', 0, 0, 0, gas, 'If both a and b are not 0, the output is 1. Otherwise 0.'),
    0x9B: ('OP_BOOLOR', 0, 0, 0, gas, 'If a or b is not 0, the output is 1. Otherwise 0.'),
    0x9C: ('OP_NUMEQUAL', 0, 0, 0, gas, 'Returns 1 if the numbers are equal, 0 otherwise.'),
    0x9E: ('OP_NUMNOTEQUAL', 0, 0, 0, gas, 'Returns 1 if the numbers are not equal, 0 otherwise.'),
    0x9F: ('OP_LESSTHAN', 0, 0, 0, gas, 'Returns 1 if a is less than b, 0 otherwise.'),
    0xA0: ('OP_GREATERTHAN', 0, 0, 0, gas, 'Returns 1 if a is greater than b, 0 otherwise.'),
    0xA1: ('OP_LESSTHANOREQUAL', 0, 0, 0, gas, 'Returns 1 if a is less than or equal to b, 0 otherwise.'),
    0xA2: ('OP_GREATERTHANOREQUAL', 0, 0, 0, gas, 'Returns 1 if a is greater than or equal to b, 0 otherwise.'),
    0xA3: ('OP_MIN', 0, 0, 0, gas, 'Returns the smaller of a and b.'),
    0xA4: ('OP_MAX', 0, 0, 0, gas, 'Returns the larger of a and b.'),
    0xA5: ('OP_WITHIN', 0, 0, 0, gas, 'Returns 1 if x is within the specified range (left-inclusive), 0 otherwise.'),

    # Crypto
    0xA6: ('OP_RIPEMD160', 0, pops, pushes, gas, 'The input is hashed using RIPEMD-160.'),
    0xA7: ('OP_SHA1', 0, pops, pushes, gas, 'The input is hashed using SHA-1.'),
    0xA8: ('OP_SHA256', 0, pops, pushes, gas, 'The input is hashed using SHA-256.'),
    0xA9: ('OP_HASH160', 0, pops, pushes, gas, 'The input is hashed twice: first with SHA-256 and then with RIPEMD-160.'),
    0xAA: ('OP_HASH256', 0, pops, pushes, gas, 'The input is hashed two times with SHA-256.'),
    0xAA: ('OP_CODESEPARATOR', 0, pops, pushes, gas, 'All of the signature checking words will only match signatures to the data after the most recently-executed OP_CODESEPARATOR.'),
    0xAC: ('OP_CHECKSIG', 0, pops, pushes, gas, 'The entire transaction\'s outputs, inputs, and script (from the most recently-executed OP_CODESEPARATOR to the end) are hashed. The signature used by OP_CHECKSIG must be a valid signature for this hash and public key. If it is, 1 is returned, 0 otherwise.'),
    0xAD: ('OP_CHECKSIGVERIFY', 0, pops, pushes, gas, 'Same as OP_CHECKSIG, but OP_VERIFY is executed afterward.'),
    0xAE: ('OP_CHECKMULTISIG', 0, pops, pushes, gas, 'Compares the first signature against each public key until it finds an ECDSA match. Starting with the subsequent public key, it compares the second signature against each remaining public key until it finds an ECDSA match. The process is repeated until all signatures have been checked or not enough public keys remain to produce a successful result. All signatures need to match a public key. Because public keys are not checked again if they fail any signature comparison, signatures must be placed in the scriptSig using the same order as their corresponding public keys were placed in the scriptPubKey or redeemScript. If all signatures are valid, 1 is returned, 0 otherwise. Due to a bug, one extra unused value is removed from the stack.'),
    0xAF: ('OP_CHECKMULTISIGVERIFY', 0, pops, pushes, gas, 'Same as OP_CHECKMULTISIG, but OP_VERIFY is executed afterward.'),

    # Locktime
    0xB1: ('OP_CHECKLOCKTIMEVERIFY', 0, pops, pushes, gas, 'Marks transaction as invalid if the top stack item is greater than the transaction\'s nLockTime field, otherwise script evaluation continues as though an OP_NOP was executed. Transaction is also invalid if 1. the stack is empty; or 2. the top stack item is negative; or 3. the top stack item is greater than or equal to 500000000 while the transaction\'s nLockTime field is less than 500000000, or vice versa; or 4. the input\'s nSequence field is equal to 0xffffffff. The precise semantics are described in BIP 0065.'),
    0xB2: ('OP_CHECKSEQUENCEVERIFY', 0, pops, pushes, gas, 'Marks transaction as invalid if the relative lock time of the input (enforced by BIP 0068 with nSequence) is not equal to or longer than the value of the top stack item. The precise semantics are described in BIP 0112.'),

    # Pseudo-words
    # These words are used internally for assisting with transaction matching. They are invalid if used in actual scripts.
    0xFA: ('OP_SMALLINTEGER', 0, pops, pushes, gas, 'OP_SMALLINTEGER'),
    0xFD: ('OP_PUBKEYS', 0, pops, pushes, gas, 'OP_PUBKEYS'),
    0xFD: ('OP_PUBKEYHASH', 0, pops, pushes, gas, 'Represents a public key hashed with OP_HASH160.'),
    0xFE: ('OP_PUBKEY', 0, pops, pushes, gas, 'Represents a public key compatible with OP_CHECKSIG.'),
    0xFF: ('OP_INVALIDOPCODE', 0, pops, pushes, gas, 'Matches any opcode that is not yet assigned.'),

    # Reserved words
    0x50: ('OP_RESERVED', 0, pops, pushes, gas, 'Transaction is invalid unless occuring in an unexecuted OP_IF branch'),
    0x62: ('OP_VER', 0, pops, pushes, gas, 'Transaction is invalid unless occuring in an unexecuted OP_IF branch'),
    0x65: ('OP_VERIF', 0, pops, pushes, gas, 'Transaction is invalid even when occuring in an unexecuted OP_IF branch'),
    0x66: ('OP_VERNOTIF', 0, pops, pushes, gas, 'Transaction is invalid even when occuring in an unexecuted OP_IF branch'),
    0x89: ('OP_RESERVED1', 0, pops, pushes, gas, 'Transaction is invalid unless occuring in an unexecuted OP_IF branch'),
    0x8A: ('OP_RESERVED2', 0, pops, pushes, gas, 'Transaction is invalid unless occuring in an unexecuted OP_IF branch'),
    0xB0: ('OP_NOP1', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
    0xB3: ('OP_NOP4', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
    0xB4: ('OP_NOP5', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
    0xB5: ('OP_NOP6', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
    0xB6: ('OP_NOP7', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
    0xB7: ('OP_NOP8', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
    0xB8: ('OP_NOP9', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
    0xB9: ('OP_NOP10', 0, 0, 0, gas, 'The word is ignored. Does not mark transaction as invalid.'),
}


class BTCScript(object):
    """Bytecode for BTC script."""

    def __init__(self):
        self.table = _table
        self.reverse_table = self._get_reverse_table()

    def _get_reverse_table(self):
        """Build an internal table used in the assembler."""
        reverse_table = {}
        for (opcode, (mnemonic, immediate_operand_size,
                      pops, pushes, gas, description)) in _table.items():
            reverse_table[mnemonic] = opcode, mnemonic, immediate_operand_size, \
                pops, pushes, gas, description

        reverse_table['OP_FALSE'] = 0x00, 'OP_FALSE', 0, 0, 1, gas, 'An empty array of bytes is pushed onto the stack.'
        reverse_table['OP_TRUE'] = 0x51, 'OP_TRUE', 0, 0, 1, gas, 'The number 1 is pushed onto the stack.'

        reverse_table['OP_1'] = 0x51, 0, 0, 1, gas, 'The number 1 is pushed onto the stack.'
        reverse_table['OP_2'] = 0x52, 0, 0, 1, gas, 'The number 2 is pushed onto the stack.'
        reverse_table['OP_3'] = 0x53, 0, 0, 1, gas, 'The number 3 is pushed onto the stack.'
        reverse_table['OP_4'] = 0x54, 0, 0, 1, gas, 'The number 4 is pushed onto the stack.'
        reverse_table['OP_5'] = 0x55, 0, 0, 1, gas, 'The number 5 is pushed onto the stack.'
        reverse_table['OP_6'] = 0x56, 0, 0, 1, gas, 'The number 6 is pushed onto the stack.'
        reverse_table['OP_7'] = 0x57, 0, 0, 1, gas, 'The number 7 is pushed onto the stack.'
        reverse_table['OP_8'] = 0x58, 0, 0, 1, gas, 'The number 8 is pushed onto the stack.'
        reverse_table['OP_9'] = 0x59, 0, 0, 1, gas, 'The number 9 is pushed onto the stack.'
        reverse_table['OP_10'] = 0x5A, 0, 0, 1, gas, 'The number 10 is pushed onto the stack.'
        reverse_table['OP_11'] = 0x5B, 0, 0, 1, gas, 'The number 11 is pushed onto the stack.'
        reverse_table['OP_12'] = 0x5C, 0, 0, 1, gas, 'The number 12 is pushed onto the stack.'
        reverse_table['OP_13'] = 0x5D, 0, 0, 1, gas, 'The number 13 is pushed onto the stack.'
        reverse_table['OP_14'] = 0x5E, 0, 0, 1, gas, 'The number 14 is pushed onto the stack.'
        reverse_table['OP_15'] = 0x5F, 0, 0, 1, gas, 'The number 15 is pushed onto the stack.'
        reverse_table['OP_16'] = 0x60, 0, 0, 1, gas, 'The number 16 is pushed onto the stack.'

        return reverse_table
