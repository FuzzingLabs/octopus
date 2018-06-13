from octopus.api.function import Function
from octopus.api.basicblock import BasicBlock
from octopus.api.edge import Edge
from octopus.api.edge import (EDGE_UNCONDITIONAL,
                              EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE,
                              EDGE_FALLTHROUGH, EDGE_CALL)
from octopus.api.cfg import CFG


from octopus.platforms.EOS.disassembler import EosDisassembler

from wasm.decode import decode_module
from wasm.modtypes import (TypeSection,
                           ImportSection,
                           FunctionSection,
                           ExportSection,
                           CodeSection)

import logging


log = logging.getLogger(__name__)
log.setLevel(level=logging.DEBUG)

# https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#language-types
language_type = {
    # Opcode, Type constructor
    -0x01: 'i32',
    -0x02: 'i64',
    -0x03: 'f32',
    -0x04: 'f64',
    -0x10: 'anyfunc',
    -0x20: 'func',
    -0x40: 'block_type'
}


def decode_type_section(type_section):
    # https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#type-section
    type_list = []

    for idx, entry in enumerate(type_section.payload.entries):

        param_str = '('
        #for _id, _x in enumerate(entry.param_types):
        #    param_str += '(param var$%d %s) ' % (_id, language_type.get(_x))
        #param_str = param_str[:-1]
        param_str += ' '.join([language_type.get(_x) for _x in entry.param_types])

        return_str = ''
        if entry.return_type:
            #return_str = ' (result %s)' % language_type.get(entry.return_type)
            return_str = ' -> %s' % language_type.get(entry.return_type)
        return_str += ')'

        type_list.append((param_str, return_str))
    return type_list


def decode_export_section(export_section):
    # https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#export-section
    export_list = []

    for idx, entry in enumerate(export_section.payload.entries):
        field_str = '\"{}\"'.format(entry.field_str.tobytes().decode('ascii'))

        # only if we export a function
        if entry.kind == 0:
            export_list.append((entry.index, field_str))
    return export_list


def enumerate_module_functions(module_bytecode):

    functions = list()

    mod_iter = iter(decode_module(module_bytecode))
    _, _ = next(mod_iter)
    sections = list(mod_iter)

    type_list = None
    import_len = 0
    function_list = None
    export_list = None
    code_data = None
    # iterate over all section
    for cur_sec, cur_sec_data in sections:
        sec = cur_sec_data.get_decoder_meta()['types']['payload']

        if isinstance(sec, TypeSection):
            type_list = decode_type_section(cur_sec_data)
        elif isinstance(sec, ImportSection):
            import_len = cur_sec_data.payload.count
        elif isinstance(sec, FunctionSection):
            function_list = cur_sec_data.payload.types
        elif isinstance(sec, ExportSection):
            export_list = decode_export_section(cur_sec_data)
        elif isinstance(sec, CodeSection):
            code_data = cur_sec_data

    for idx, func in enumerate(code_data.payload.bodies):

        param_str, return_str = type_list[function_list[idx]]
        func_id = import_len + idx
        name = '$func%d %s%s' % (func_id, param_str, return_str)
        prefered_name = ''
        if export_list:
            for index, field_str in export_list:
                if index == func_id:
                    #prefered_name = '%s %s%s' % (field_str, param_str, return_str)
                    prefered_name = '%s' % (field_str)
                    break
        instructions = EosDisassembler().disassemble(func.code.tobytes())
        cur_function = Function(0, instructions[0], name=name, prefered_name=prefered_name)
        cur_function.instructions = instructions

        functions.append(cur_function)
    return functions


def bb_name_format(function_id, offset):
    return ('block_%x_%x' % (function_id, offset))


def enumerate_basicblocks_edges(function_id, instructions):

    """
    Return a list of basicblock after
    statically parsing given instructions
    """

    basicblocks = list()
    edges = list()
    labels = []

    intent = 0
    # find label first
    for index, inst in enumerate(instructions):
        if inst.is_block_starter:
            if inst.name in ['block', 'loop']:
                intent += 1
        elif inst.name in ['end']:
            if intent > 0:
                intent -= 1
                #tmp_labels.append({'intent': intent,
                #                   'offset': inst.offset_end})
                labels.append(inst.offset_end)
    # print(function_id)
    # print(labels)
    '''
    #e = [{'intent': 0, 'offset': 15}, {'intent': 1, 'offset': 17}, {'intent': 0, 'offset': 56}]
    tmp_list = []
    for index, x in enumerate(tmp_labels):
        if x.get('intent') == 0:
            labels += tmp_list[::-1]
            tmp_list = []
        tmp_list.append(x.get('offset'))
    labels += tmp_list[::-1]
    print(labels)
    '''

    # remove "block" instruction - not usefull graphicaly
    instructions = [x for x in instructions if x.name not in ['block', 'loop']]
    # create the first block
    new_block = False
    end_block = False
    block = BasicBlock(instructions[0].offset,
                       instructions[0],
                       name=bb_name_format(function_id, instructions[0].offset))

    for index, inst in enumerate(instructions):
        if new_block:
            block = BasicBlock(inst.offset,
                               inst,
                               name=bb_name_format(function_id, inst.offset))
            new_block = False

        # add current instruction to the basicblock
        block.instructions.append(inst)

        # absolute jump - br
        # br is *always* followed by end instruction

        if inst.is_branch_unconditional:
            end_block = True
            jump_offset = int(inst.operand_interpretation.split(' ')[1])
            if instructions[index + 1].name == 'end':
                end_block = False
            edges.append(Edge(block.name, bb_name_format(function_id, labels[jump_offset]  + 1), EDGE_UNCONDITIONAL))

        # conditionnal jump - br_if
        elif inst.is_branch_conditional:
            end_block = True
            jump_offset = int(inst.operand_interpretation.split(' ')[1])
            edges.append(Edge(block.name, bb_name_format(function_id, labels[jump_offset] + 1), EDGE_CONDITIONAL_TRUE))
            edges.append(Edge(block.name, bb_name_format(function_id, instructions[index + 1].offset), EDGE_CONDITIONAL_FALSE))

        # end of a block
        elif index < (len(instructions) - 1) and \
                inst.name in ['end', 'else']:  # is_block_terminator
            end_block = True
            if not instructions[index - 1].is_branch_unconditional:
                edges.append(Edge(block.name, bb_name_format(function_id, instructions[index + 1].offset), EDGE_FALLTHROUGH))

        # start of a block
        elif index < (len(instructions) - 1) and \
                instructions[index + 1].is_block_starter:
            end_block = True
            edges.append(Edge(block.name, bb_name_format(function_id, instructions[index + 1].offset), EDGE_FALLTHROUGH))

        # last instruction of the entire bytecode
        elif inst == instructions[-1]:
            end_block = True

        if end_block:
            block.end_offset = inst.offset_end
            block.end_instr = inst
            basicblocks.append(block)
            new_block = True
            end_block = False

    edges = list(set(edges))
    return basicblocks, edges


class EosCFG(CFG):
    """
    TODO: fix some CFG issue related to block/end/if/else/end instructions
    """
    def __init__(self, module_bytecode, static_analysis=True):

        self.module_bytecode = module_bytecode
        self.static_analysis = static_analysis

        self.functions = list()
        self.basicblocks = list()
        self.edges = list()

        if self.static_analysis:
            self.run_static_analysis()

    def run_static_analysis(self):
        self.functions = enumerate_module_functions(self.module_bytecode)
        # print(self.functions)
        # for i in self.functions:
        #    print(i.prefered_name)

        for idx, func in enumerate(self.functions):
            func.basicblocks, edges = enumerate_basicblocks_edges(idx, func.instructions)
            # all bb name are unique so we can create global bb & edge list
            self.basicblocks += func.basicblocks
            self.edges += edges

    def show(self):
        print("len func = %d" % len(self.functions))
        print("len edges = %d" % len(self.edges))
