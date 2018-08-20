#
# Title: WebAssembly module analysis
#
# Date: 20/08/18
#
# Author: Patrick Ventuzelo - @Pat_Ventuzelo
#

from octopus.arch.wasm.analyzer import WasmModuleAnalyzer

# complete wasm module
file_name = "examples/wasm/samples/hello_wasm_studio.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the WasmModuleAnalyzer
# analysis set to True by default
an = WasmModuleAnalyzer(raw, analysis=True)

print('list functions:')
print(an.func_prototypes)
print()

# detect if wasm module contains emscripten syscalls
print('contains emscripten syscalls ?')
print(an.contains_emscripten_syscalls())
