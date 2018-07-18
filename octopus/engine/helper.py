#from .constants import TT256, TT255

import re
from z3 import *

TT256 = 2 ** 256
TT256M1 = 2 ** 256 - 1
TT255 = 2 ** 255


class helper(object):

    def is_symbolic(value):
        return not isinstance(value, int)

    def is_real(value):
        return isinstance(value, int)

    def isAllReal(*args):
        for i in args:
            if is_symbolic(i):
                return False
        return True

    def safe_decode(hex_encoded_string):

        if (hex_encoded_string.startswith("0x")):
            return bytes.fromhex(hex_encoded_string[2:])
        else:
            return bytes.fromhex(hex_encoded_string)

    def to_signed(i):
        return i if i < TT255 else i - TT256

    def get_trace_line(instr, state):

        stack = str(state.stack[::-1])

        # stack = re.sub("(\d+)",    lambda m: hex(int(m.group(1))), stack)
        stack = re.sub("\n", "", stack)

        return str(instr['address']) + " " + instr['opcode'] + "\tSTACK: " + stack

    def convert_to_bitvec(item):
        # converting boolean expression to bitvector
        if type(item) == BoolRef:
            return If(item, BitVecVal(1, 256), BitVecVal(0, 256))
        elif type(item) == bool:
            if item:
                return BitVecVal(1, 256)
            else:
                return BitVecVal(0, 256)
        elif type(item) == int:
            return BitVecVal(item, 256)
        else:
            return simplify(item)

    def convert_to_concrete_int(item):
        if (type(item) == int):
            return item

        if (type(item) == BitVecNumRef):
            return item.as_long()

        return simplify(item).as_long()

    def get_concrete_int(item):

        if (type(item) == int):
            return item

        if (type(item) == BitVecNumRef):
            return item.as_long()

        return simplify(item).as_long()

    def concrete_int_from_bytes(_bytes, start_index):

        # logging.debug("-- concrete_int_from_bytes: " + str(_bytes[start_index:start_index+32]))
        b = _bytes[start_index:start_index+32]

        val = int.from_bytes(b, byteorder='big')

        return val

    def concrete_int_to_bytes(val):

        # logging.debug("concrete_int_to_bytes " + str(val))

        if (type(val) == int):
            return val.to_bytes(32, byteorder='big')

        return (simplify(val).as_long()).to_bytes(32, byteorder='big')
