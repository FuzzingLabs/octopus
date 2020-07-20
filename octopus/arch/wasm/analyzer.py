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
                           DataSection,
                           NameSubSection,
                           # Name subsection types.
                           NAME_SUBSEC_FUNCTION,
                           NAME_SUBSEC_LOCAL)

from octopus.arch.wasm.constant import LANG_TYPE, KIND_TYPE
from octopus.arch.wasm.format import (format_kind_function,
                                      format_kind_table,
                                      format_kind_memory,
                                      format_kind_global)

from wasm.decode import decode_module
from octopus.core.utils import bytecode_to_bytes

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
        return str(self.show())

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
        mod_iter = iter(decode_module(self.module_bytecode, True))
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


    def __decode_name_section(self, name_subsection):
        """
        .. seealso:: https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#name-section
        """
        names_list = list()

        if name_subsection.name_type == NAME_SUBSEC_FUNCTION:
            subsection_function = name_subsection.payload
            for name in subsection_function.names:
                try:
                    name_str = name.name_str.tobytes().decode('utf-8')
                except UnicodeDecodeError:
                    name_str = name.name_str.tobytes()
                names_list.append((name.index, name.name_len, name_str))

        elif name_subsection.name_type == NAME_SUBSEC_LOCAL:
            print("__decode_name_section NAME_SUBSEC_LOCAL not implemented")

        else:
            print("__decode_name_section name_type unknown")

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
            func_prototypes.append((name, _param, _return, 'import'))

        # get all internal functions
        for idx, code in enumerate(self.codes):
            _param, _return = self.types[self.func_types[idx]]
            real_index = len(self.imports_func) + idx
            name = '$func%d' % real_index
            f_type = 'local'

            # if exported function - overwrite name
            for x in self.exports:
                if x.get('index') == real_index and x.get('kind') == 0:
                    name = x.get('field_str')
                    f_type = 'export'

            for name_index, _, name_str in self.names:
                if real_index == name_index:
                    name = name_str

            # TODO: need to test
            if real_index == self.start:
                name = '* ' + name
            func_prototypes.append((name, _param, _return, f_type))
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

        mod_iter = iter(decode_module(self.module_bytecode, True))
        # decode header version - usefull in the future (multiple versions)
        header, header_data = next(mod_iter)
        self.magic, self.version = self.__decode_header(header, header_data)

        #
        # Wasm sections
        #

        for cur_sec, cur_sec_data in mod_iter:
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
            # name section
            elif isinstance(cur_sec, NameSubSection):
                self.names = self.__decode_name_section(cur_sec_data)
            else:
                self.customs.append(self.__decode_unknown_section(cur_sec_data))

        # create ordered list of functions
        self.func_prototypes = self.get_func_prototypes_ordered()
        return True

    def is_compiled_with_emscripten(self):
        matching_list = self.get_emscripten_calls()
        return True if matching_list else False

    def get_emscripten_calls(self):
        res = [x for x, _, _, _ in self.func_prototypes if is_emscripten_func(x)]
        return res

    # emscripten syscall from:
    # * https://github.com/kripken/emscripten/blob/incoming/system/lib/fetch/asmfs.cpp
    # * http://gauss.ececs.uc.edu/Courses/c4029/code/syscall_32.tbl.html
    def contains_emscripten_syscalls(self):
        EMSCRIPTEN_SYSCALL_JSON = '/signatures/emscripten_syscalls.json'
        path = os.path.dirname(os.path.realpath(__file__)) + EMSCRIPTEN_SYSCALL_JSON

        json_data = open(path).read()
        data = json.loads(json_data)

        func_names = [x for x, _, _, _ in self.func_prototypes]
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
        'SAFE_HEAP_LOAD', 'SAFE_HEAP_LOAD_D',
        'SAFE_HEAP_STORE', 'SAFE_HEAP_STORE_D', 'SAFE_FT_MASK',
        # create_receiving
        '_memcpy', '_memset', 'runPostSets',
        '_emscripten_replace_memory', '__start_module',
        # create_asm_runtime_funcs
        'stackAlloc', 'stackSave',
        'stackRestore', 'establishStackSpace', 'setThrew',
        'setTempRet0', 'getTempRet0',
        'setDynamicTop',
        'emterpret',
        'setAsyncState', 'emtStackSave',
        'emtStackRestore', 'getEmtStackMax', 'setEmtStackMax',
        'setAsync',
        'addOnExit',
        # from emscripten/emcc.py
        '_stbi_load', '_stbi_load_from_memory', '_stbi_image_free',
        '___cxa_demangle',
        '_malloc', '_free',
        'allocate', 'getMemory',
        '___errno_location', '_fflush',
        'FS_createFolder',
        'FS_createPath',
        'FS_createDataFile',
        'FS_createPreloadedFile',
        'FS_createLazyFile',
        'FS_createLink',
        'FS_createDevice',
        'FS_unlink',
        'addRunDependency',
        'removeRunDependency',
        # from emscripten/tools/ctor_evaller.py
        '_sbrk', '___cxa_atexit', '_atexit', 'dumpGlobals',
        # from emscripten/system/lib/pthreads.symbols
        '___assert_fail', '___errno_location', '___lock',
        '___pthread_self', '___pthread_tsd_main',
        '___pthread_tsd_run_dtors', '___pthread_tsd_size',
        '___shm_mapname', '___timedwait', '___unlock',
        '___vm_lock', '___vm_lock_impl', '___vm_unlock',
        '___vm_unlock_impl', '___wait', '__pthread_getcanceltype',
        '__pthread_isduecanceled', '__pthread_msecs_until',
        '____atomic_is_lock_free', '__llvm_atomic_load_add_i32_p0i32',
        '__llvm_memory_barrier', '_accept', '_access',
        '_atexit', '_bind', '_calloc', '_chdir', '_chmod',
        '_chown', '_chroot', '_clearenv', '_clearerr',
        '_clock_gettime', '_close', '_closedir', '_confstr',
        '_connect', '_creat', '_crypt', '_ctermid', '_dprintf',
        '_dup', '_dup2', '_emscripten_asm_const',
        '_emscripten_futex_wait', '_emscripten_futex_wake',
        '_emscripten_get_now', '_emscripten_is_main_runtime_thread',
        '_emscripten_main_thread_process_queued_calls',
        '_emscripten_pthread_attr_settransferredcanvases',
        '_emscripten_pthread_attr_gettransferredcanvases',
        '_emscripten_sync_run_in_main_thread',
        '_emscripten_sync_run_in_main_thread_0',
        '_emscripten_sync_run_in_main_thread_1',
        '_emscripten_sync_run_in_main_thread_2',
        '_emscripten_sync_run_in_main_thread_3',
        '_emscripten_sync_run_in_main_thread_4',
        '_emscripten_sync_run_in_main_thread_5',
        '_emscripten_sync_run_in_main_thread_6',
        '_emscripten_sync_run_in_main_thread_xprintf_varargs',
        '_encrypt', '_fchdir', '_fchmod', '_fchown', '_fclose',
        '_fcntl', '_fdopen', '_feof', '_ferror', '_fflush',
        '_fgetc', '_fgetpos', '_fgets', '_fileno', '_fopen',
        '_fpathconf', '_fprintf', '_fputc', '_fputs', '_fread',
        '_free', '_freopen', '_fscanf', '_fseek', '_fsetpos',
        '_fstat', '_fstatvfs', '_fsync', '_ftell', '_ftruncate',
        '_fwrite', '_getchar', '_getcwd', '_getenv',
        '_gethostname', '_getlogin', '_getlogin_r',
        '_getpeername', '_gets', '_getsockname', '_getsockopt',
        '_gettimeofday', '_ioctl', '_isatty', '_lchmod',
        '_lchown', '_link', '_listen', '_lockf', '_lseek',
        '_lstat', '_malloc', '_mkdir', '_mkdtemp', '_mkfifo',
        '_mknod', '_mkstemp', '_mktemp', '_mmap', '_munmap',
        '_nanosleep', '_open', '_opendir', '_pclose',
        '_perror', '_pipe', '_poll', '_popen', '_posix_fallocate',
        '_pread', '_printf', '_pthread_attr_destroy',
        '_pthread_attr_getdetachstate', '_pthread_attr_getguardsize',
        '_pthread_attr_getinheritsched', '_pthread_attr_getschedparam',
        '_pthread_attr_getschedpolicy', '_pthread_attr_getscope',
        '_pthread_attr_getstack', '_pthread_attr_getstacksize',
        '_pthread_attr_init', '_pthread_attr_setdetachstate',
        '_pthread_attr_setguardsize', '_pthread_attr_setinheritsched',
        '_pthread_attr_setschedparam', '_pthread_attr_setschedpolicy',
        '_pthread_attr_setscope', '_pthread_attr_setstack',
        '_pthread_attr_setstacksize', '_pthread_barrier_destroy',
        '_pthread_barrier_init', '_pthread_barrier_wait',
        '_pthread_barrierattr_destroy',
        '_pthread_barrierattr_getpshared',
        '_pthread_barrierattr_init',
        '_pthread_barrierattr_setpshared',
        '_pthread_cleanup_pop',
        '_pthread_cleanup_push',
        '_pthread_cond_broadcast', '_pthread_cond_destroy',
        '_pthread_cond_init', '_pthread_cond_signal',
        '_pthread_cond_timedwait', '_pthread_cond_wait',
        '_pthread_condattr_destroy', '_pthread_condattr_getclock',
        '_pthread_condattr_getpshared', '_pthread_condattr_init',
        '_pthread_condattr_setclock',
        '_pthread_condattr_setpshared', '_pthread_create',
        '_pthread_equal', '_pthread_getattr_np',
        '_pthread_getspecific', '_pthread_key_create',
        '_pthread_key_delete', '_pthread_mutex_consistent',
        '_pthread_mutex_destroy', '_pthread_mutex_getprioceiling',
        '_pthread_mutex_init', '_pthread_mutex_lock',
        '_pthread_mutex_setprioceiling', '_pthread_mutex_timedlock',
        '_pthread_mutex_trylock', '_pthread_mutex_unlock',
        '_pthread_mutexattr_destroy',
        '_pthread_mutexattr_getprotocol',
        '_pthread_mutexattr_getpshared',
        '_pthread_mutexattr_getrobust',
        '_pthread_mutexattr_gettype', '_pthread_mutexattr_init',
        '_pthread_mutexattr_setprotocol',
        '_pthread_mutexattr_setpshared',
        '_pthread_mutexattr_setrobust',
        '_pthread_mutexattr_settype', '_pthread_once',
        '_pthread_rwlock_destroy', '_pthread_rwlock_init',
        '_pthread_rwlock_rdlock', '_pthread_rwlock_timedrdlock',
        '_pthread_rwlock_timedwrlock',
        '_pthread_rwlock_tryrdlock', '_pthread_rwlock_trywrlock',
        '_pthread_rwlock_unlock', '_pthread_rwlock_wrlock',
        '_pthread_rwlockattr_destroy',
        '_pthread_rwlockattr_getpshared',
        '_pthread_rwlockattr_init',
        '_pthread_rwlockattr_setpshared', '_pthread_self',
        '_pthread_setcancelstate', '_pthread_setcanceltype',
        '_pthread_setspecific', '_pthread_spin_destroy',
        '_pthread_spin_init', '_pthread_spin_lock',
        '_pthread_spin_trylock', '_pthread_spin_unlock',
        '_pthread_testcancel', '_putchar', '_putenv',
        '_puts', '_pwrite', '_read', '_readdir', '_readdir_r',
        '_readlink', '_realpath', '_recv', '_recvfrom',
        '_recvmsg', '_remove', '_rename', '_rewind', '_rewinddir',
        '_rmdir', '_sbrk', '_scanf', '_sched_get_priority_max',
        '_sched_get_priority_min', '_seekdir', '_select',
        '_sem_close', '_sem_destroy', '_sem_getvalue',
        '_sem_init', '_sem_open', '_sem_post', '_sem_timedwait',
        '_sem_trywait', '_sem_unlink', '_sem_wait', '_send',
        '_sendmsg', '_sendto', '_setenv', '_shm_unlink',
        '_shutdown', '_snprintf', '_socket', '_stat', '_statvfs',
        '_symlink', '_sysconf', '_tcgetattr', '_tcsetattr',
        '_telldir', '_tempnam', '_tmpfile', '_tmpnam',
        '_truncate', '_ttyname', '_ttyname_r', '_tzset',
        '_umask', '_ungetc', '_unlink', '_unsetenv', '_usleep',
        '_utime', '_utimes', '_vsnprintf', '_write']

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
