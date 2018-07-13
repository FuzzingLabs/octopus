"""Defines immediate types for WASM bytecode instructions."""
from __future__ import print_function, absolute_import, division, unicode_literals

from .wasmtypes import *
from .types import Structure, RepeatField


class BlockImm(Structure):
    sig = BlockTypeField()


class BranchImm(Structure):
    relative_depth = VarUInt32Field()


class BranchTableImm(Structure):
    target_count = VarUInt32Field()
    target_table = RepeatField(VarUInt32Field(), lambda x: x.target_count)
    default_target = VarUInt32Field()


class CallImm(Structure):
    function_index = VarUInt32Field()


class CallIndirectImm(Structure):
    type_index = VarUInt32Field()
    reserved = VarUInt1Field()


class LocalVarXsImm(Structure):
    local_index = VarUInt32Field()


class GlobalVarXsImm(Structure):
    global_index = VarUInt32Field()


class MemoryImm(Structure):
    flags = VarUInt32Field()
    offset = VarUInt32Field()


class CurGrowMemImm(Structure):
    reserved = VarUInt1Field()


class I32ConstImm(Structure):
    value = VarInt32Field()


class I64ConstImm(Structure):
    value = VarInt64Field()


class F32ConstImm(Structure):
    value = UInt32Field()


class F64ConstImm(Structure):
    value = UInt64Field()
