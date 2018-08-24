from wasm.modtypes import (TypeSection,
                           ImportSection,
                           FunctionSection,
                           TableSection,
                           MemorySection,
                           GlobalSection,
                           ExportSection,
                           StartSection,
                           ElementSection,
                           CodeSection,
                           DataSection)

from octopus.arch.wasm.constant import LANG_TYPE, KIND_TYPE
from octopus.arch.wasm.format import (format_kind_function,
                                      format_kind_table,
                                      format_kind_memory,
                                      format_kind_global)

from octopus.arch.wasm.decode import decode_module

from octopus.core.utils import bytecode_to_bytes
# from wasm.decode import decode_module
import io
import json
import os

from logging import getLogger
logging = getLogger(__name__)


class WasmModuleAnalyzer(object):
    '''Analyze and extract informations from wasm module'''

    def __init__(self, module_bytecode, analysis=True):
        self.module_bytecode = bytecode_to_bytes(module_bytecode)

        self.magic = None
        self.version = None
        self.types = list()
        self.imports_all = list()
        self.imports_func = list()
        self.func_types = list()
        self.tables = list()
        self.memories = list()
        self.globals = list()
        self.exports = list()
        self.start = None
        self.elements = list()
        self.codes = list()
        self.datas = list()
        self.names = list()
        self.customs = list()
        self.func_prototypes = list()
        # self.strings = list() - TODO

        if analysis:
            self.analyze()

    def attributes_reset(self):
        self.magic = None
        self.version = None
        self.types = list()
        self.imports_all = list()
        self.imports_func = list()
        self.func_types = list()
        self.tables = list()
        self.memories = list()
        self.globals = list()
        self.exports = list()
        self.start = None
        self.elements = list()
        self.codes = list()
        self.datas = list()
        self.names = list()
        self.customs = list()
        self.func_prototypes = list()

    def __str__(self):
        return self.show()

    def show(self):
        """Return dict with WasmModuleAnalyzer attributes"""
        return {'magic': self.magic,
                'version': self.version,
                'types': self.types,
                'imports_all': self.imports_all,
                'imports_func': self.imports_func,
                'func_types': self.func_types,
                'tables': self.tables,
                'memories': self.memories,
                'globals': self.globals,
                'exports': self.exports,
                'start': self.start,
                'elements': self.elements,
                'length codes': len(self.codes),
                'datas': self.datas,
                'func_prototypes': self.func_prototypes}

    def __get_section(self, section_type):
        mod_iter = iter(decode_module(self.module_bytecode))
        _, _ = next(mod_iter)
        sections = list(mod_iter)

        # iterate over all section
        for cur_sec, cur_sec_data in sections:
            sec = cur_sec_data.get_decoder_meta()['types']['payload']

            if isinstance(sec, section_type):
                return cur_sec_data
        return None

    def __decode_header(self, header, h_data):
        """Decode wasm header
        Return tuple (magic, version) of wasm module header
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#high-level-structure
        """
        magic = \
            h_data.magic.to_bytes(header.magic.byte_size, 'little')
        version = \
            h_data.version.to_bytes(header.version.byte_size, 'little')
        return (magic, version)

    def __decode_type_section(self, type_section):
        """Decode wasm type section
        Return a list of tuple (param_str, return_str)
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#type-section
        """
        type_list = []

        for idx, entry in enumerate(type_section.payload.entries):
            param_str = ''
            return_str = ''

            param_str += ' '.join([LANG_TYPE.get(_x) for _x in entry.param_types])
            if entry.return_type:
                return_str = '%s' % LANG_TYPE.get(entry.return_type)

            type_list.append((param_str, return_str))
        return type_list

    def __decode_import_section(self, import_section):
        """Decode import section to tuple of list
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#import-section
        """
        entries = import_section.payload.entries
        import_list = []
        import_func_list = []

        for idx, entry in enumerate(entries):
            #            for encoding in ('utf-8', 'utf-16-be'):
            #                value = str(v)
            #                try:
            #                    value = v.decode(encoding)
            #                    break
            #                except UnicodeDecodeError:
            #                    value = str(v)
            try:
                module_str = entry.module_str.tobytes().decode('utf-8')
            except UnicodeDecodeError:
                module_str = entry.module_str.tobytes()
            try:
                field_str = entry.field_str.tobytes().decode('utf-8')
            except UnicodeDecodeError:
                field_str = entry.field_str.tobytes()

            logging.debug('%s %s', module_str, field_str)
            kind_type = KIND_TYPE.get(entry.kind)

            if kind_type == 'function':
                f_type = format_kind_function(entry.type.type)
                import_list.append((entry.kind, module_str, field_str, f_type))
                # add also the info into the specific import function list
                import_func_list.append((module_str, field_str, f_type))
            elif kind_type == 'table':
                tabl = format_kind_table(entry.type.element_type,
                                         entry.type.limits.flags,
                                         entry.type.limits.initial,
                                         entry.type.limits.maximum)
                import_list.append((entry.kind, module_str, field_str, tabl))

            elif kind_type == 'memory':
                mem = format_kind_memory(entry.type.limits.flags,
                                         entry.type.limits.initial,
                                         entry.type.limits.maximum)
                import_list.append((entry.kind, module_str, field_str, mem))

            elif kind_type == 'global':
                gbl = format_kind_global(entry.type.content_type,
                                         entry.type.mutability)
                import_list.append((entry.kind, module_str, field_str, gbl))
            else:
                logging.error('unknown %d %s %s', entry.kind,
                              module_str, field_str)
        return (import_list, import_func_list)

    def __decode_function_section(self, function_section):
        """Decode function section
        The function section declares the signatures of all functions in the module
        Return list of indices (int)
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#function-section
        """
        return function_section.payload.types

    def __decode_table_section(self, table_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#table-section
        """
        # on the MVP, table size == 1
        entries = table_section.payload.entries
        table_list = []

        for idx, entry in enumerate(entries):
            element_type = entry.element_type
            flags = entry.limits.flags
            initial = entry.limits.initial
            maximum = entry.limits.maximum

            fmt = format_kind_table(element_type,
                                    flags,
                                    initial,
                                    maximum)
            table_list.append(fmt)
        return table_list

    def __decode_memory_section(self, memory_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#memory-section
        """
        # on the MVP, memory size == 1
        memory_l = list()
        entries = memory_section.payload.entries

        for idx, entry in enumerate(entries):

            flags = entry.limits.flags
            initial = entry.limits.initial
            maximum = entry.limits.maximum

            fmt = format_kind_memory(flags,
                                     initial,
                                     maximum)

            memory_l.append(fmt)
        return memory_l

    def __decode_global_section(self, global_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#global-section
        """
        globals_l = list()
        for entry in global_section.payload.globals:
            fmt = format_kind_global(entry.type.mutability,
                                     entry.type.content_type)
            globals_l.append(fmt)
        return globals_l

    def __decode_export_section(self, export_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#export-section
        """
        entries = export_section.payload.entries
        export_list = []

        for idx, entry in enumerate(entries):
            # field_str == function_name
            try:
                field_str = entry.field_str.tobytes().decode('utf-8')
            except UnicodeDecodeError:
                field_str = entry.field_str.tobytes()
            kind = entry.kind
            index = entry.index

            fmt = {'field_str': field_str,
                   'kind': kind,
                   'index': index}
            export_list.append(fmt)
        return export_list

    def __decode_start_section(self, start_section):
        return start_section.payload.index

    def __decode_element_section(self, element_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#element-section
        """
        entries = element_section.payload.entries
        element_list = []

        for idx, entry in enumerate(entries):

            fmt = {'index': entry.index,
                   'offset': entry.offset,
                   'elems': entry.elems}

            element_list.append(fmt)
        return element_list

    def __decode_code_section(self, code_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#code-section
        """
        bodies = code_section.payload.bodies
        code_list = []

        for idx, entry in enumerate(bodies):
            code_raw = entry.code.tobytes()
            code_list.append(code_raw)
        return code_list

    def __decode_data_section(self, data_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#data-section
        """
        entries = data_section.payload.entries
        data_list = []

        for idx, entry in enumerate(entries):
            data = entry.data.tobytes()

            fmt = {'index': entry.index,
                   'offset': entry.offset,
                   'size': entry.size,
                   'data': data}

            data_list.append(fmt)
        return data_list

    def __decode_name_section(self, name_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#name-section
        """
        payload = name_section.payload.tobytes()
        total = 0
        names_list = list()

        f = io.BytesIO(payload)
        count = int.from_bytes(f.read(1), byteorder='big')
        total += 1

        while total < len(payload) - 1:
            index = int.from_bytes(f.read(1), byteorder='big')
            total += 1
            name_len = int.from_bytes(f.read(1), byteorder='big')
            total += 1
            name_str = f.read(name_len)
            total += name_len
            names_list.append((index, name_len, name_str))
        f.close()
        return names_list

    def __decode_unknown_section(self, unknown_section):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#high-level-structure
        """
        sec_name = unknown_section.name.tobytes()
        payload = unknown_section.payload.tobytes()
        return (sec_name, payload)

    def get_func_prototypes_ordered(self):
        """create ordered list of functions"""

        func_prototypes = list()

        # get imported functions
        for _, name, type_idx in self.imports_func:
            _param, _return = self.types[type_idx]
            func_prototypes.append((name, _param, _return))

        # get all internal functions
        for idx, code in enumerate(self.codes):
            _param, _return = self.types[self.func_types[idx]]
            real_index = len(self.imports_func) + idx
            name = '$func%d' % real_index

            # if exported function - overwrite name
            for x in self.exports:
                if x.get('index') == real_index and x.get('kind') == 0:
                    name = x.get('field_str')

            # TODO: need to test
            if real_index == self.start:
                name = '* ' + name
            func_prototypes.append((name, _param, _return))
        return func_prototypes

    def analyze(self):
        """analyse the complete module & extract informations """
        # src: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md
        # custom     0   name, .debug_str, ...
        # Type       1   Function signature declarations
        # Import     2   Import declarations
        # Function   3   Function declarations
        # Table      4   Indirect function table and other tables
        # Memory     5   Memory attributes
        # Global     6   Global declarations
        # Export     7   Exports
        # Start      8   Start function declaration
        # Element    9   Elements section
        # Code       10  Function bodies (code)
        # Data       11  Data segments

        # reset attributes
        self.attributes_reset()

        mod_iter = iter(decode_module(self.module_bytecode))
        # decode header version - usefull in the future (multiple versions)
        header, header_data = next(mod_iter)
        self.magic, self.version = self.__decode_header(header, header_data)

        #
        # Wasm sections
        #
        sections = list(mod_iter)

        for cur_sec, cur_sec_data in sections:
            sec = cur_sec_data.get_decoder_meta()['types']['payload']

            if isinstance(sec, TypeSection):
                self.types = self.__decode_type_section(cur_sec_data)
            elif isinstance(sec, ImportSection):
                self.imports_all, self.imports_func = \
                    self.__decode_import_section(cur_sec_data)
            elif isinstance(sec, FunctionSection):
                self.func_types = self.__decode_function_section(cur_sec_data)
            elif isinstance(sec, TableSection):
                self.tables = self.__decode_table_section(cur_sec_data)
            elif isinstance(sec, MemorySection):
                self.memories = self.__decode_memory_section(cur_sec_data)
            elif isinstance(sec, GlobalSection):
                # TODO not analyzed
                self.globals = self.__decode_global_section(cur_sec_data)
            elif isinstance(sec, ExportSection):
                self.exports = self.__decode_export_section(cur_sec_data)
            elif isinstance(sec, StartSection):
                # TODO not analyzed
                self.start = self.__decode_start_section(cur_sec_data)
            elif isinstance(sec, ElementSection):
                self.elements = self.__decode_element_section(cur_sec_data)
            elif isinstance(sec, CodeSection):
                self.codes = self.__decode_code_section(cur_sec_data)
            elif isinstance(sec, DataSection):
                self.datas = self.__decode_data_section(cur_sec_data)
            else:
                # name section
                if cur_sec_data.id == 0 and cur_sec_data.name.tobytes() == b'name':
                    self.names = self.__decode_name_section(cur_sec_data)
                else:
                    # TODO - handle properly .debug_str section
                    self.customs.append(self.__decode_unknown_section(cur_sec_data))

        # create ordered list of functions
        self.func_prototypes = self.get_func_prototypes_ordered()
        return True

    def is_compiled_with_emscripten(self):
        matching_list = self.get_emscripten_calls()
        return True if matching_list else False

    def get_emscripten_calls(self):
        res = [x for x, _, _ in self.func_prototypes if is_emscripten_func(x)]
        return res

    # emscripten syscall from:
    # * https://github.com/kripken/emscripten/blob/incoming/system/lib/fetch/asmfs.cpp
    # * http://gauss.ececs.uc.edu/Courses/c4029/code/syscall_32.tbl.html
    def contains_emscripten_syscalls(self):
        EMSCRIPTEN_SYSCALL_JSON = '/signatures/emscripten_syscalls.json'
        path = os.path.dirname(os.path.realpath(__file__)) + EMSCRIPTEN_SYSCALL_JSON

        json_data = open(path).read()
        data = json.loads(json_data)

        func_names = [x for x, _, _ in self.func_prototypes]
        match = list()
        for name in func_names:
            try:
                # remove '_' to match '__syscallXX' & '___syscallXX'
                syscall = data[name.replace('_', '')]
                match.append((name, syscall))
            except KeyError:
                pass
        return match


def is_emscripten_func(x):

    # from https://github.com/kripken/emscripten/blob/master/emscripten.py
    EMSCRIPTEN_LIST = [
        # create_basic_funcs
        'abort', 'assert', 'enlargeMemory', 'getTotalMemory',
        'abortOnCannotGrowMemory',
        'abortStackOverflow',
        'abortStackOverflowEmterpreter',
        'segfault', 'alignfault', 'ftfault',
        'SAFE_HEAP_LOAD', 'SAFE_HEAP_LOAD_D', 'SAFE_HEAP_STORE', 'SAFE_HEAP_STORE_D', 'SAFE_FT_MASK',
        # create_receiving
        '_memcpy', '_memset', 'runPostSets', '_emscripten_replace_memory', '__start_module',
        # create_asm_runtime_funcs
        'stackAlloc', 'stackSave', 'stackRestore', 'establishStackSpace', 'setThrew',
        'setTempRet0', 'getTempRet0',
        'setDynamicTop',
        'emterpret',
        'setAsyncState', 'emtStackSave', 'emtStackRestore', 'getEmtStackMax', 'setEmtStackMax'
        'setAsync']

    if x.startswith('_emscripten_'):
        return True
    # function_tables(...)
    elif x.startswith('dynCall_'):
        return True
    # create_basic_funcs(...)
    elif x.startswith('nullFunc_'):
        return True
    elif x.startswith('invoke_'):
        return True
    elif x.startswith('jsCall_'):
        return True
    elif x.startswith('ftCall_'):
        return True
    # syscalls
    elif x.replace('_', '').startswith('syscall'):
        return True
    elif x in EMSCRIPTEN_LIST:
        return True
    else:
        return False
