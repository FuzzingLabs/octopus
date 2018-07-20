# Octopus
[![Generic badge](https://img.shields.io/badge/REcon-MTL%202018-red.svg)](https://recon.cx/2018/montreal/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/quoscient/octopus/graphs/commit-activity)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE.md)

<p align="center">
	<img src="/images/logo-medium.png" height="400px"/>
</p>

**Octopus is a security analysis framework for WebAssembly and Blockchain Smart Contract.**

The purpose of Octopus is to provide an easy way to analyze smart contract security and understand better what is really stored on the blockchain.


## Features

- **Explorer**: Octopus JSON-RPC client implementation to communicate with platforms blockchains
- **Disassembler**: Octopus can translate bytecode into assembly representation
- **Control Flow Analysis**: Octopus can generate a Control Flow Graph (CFG) 
- **Call Flow Analysis**: Octopus can generate a Call Flow Graph (function level) 
- **IR conversion (SSA)**: Octopus can simplify assembly into Static Single Assignment (SSA) representation
- **Symbolic Execution**: Octopus can use symbolic execution to find new paths into a program

## Platforms / Architectures

Octopus support the following types of programs/smart contracts:
* WebAssembly module (WASM)
* Bitcoin script (BTC script)
* Ethereum smart contracts (EVM bytecode)
* EOS smart contracts (WASM)
* NEO smart contracts (AVM bytecode)


|| BTC | ETH | EOS | NEO || WASM
|:--------------------:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Explorer** | :heavy_check_mark: | :heavy_check_mark:| :heavy_check_mark: | :heavy_check_mark: | | :o: |
|**Disassembler** | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | :heavy_check_mark: |
|**Control Flow Analysis** | :heavy_multiplication_x: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | :heavy_check_mark: |
|**Call Flow Analysis** | :heavy_multiplication_x: | :heavy_plus_sign: | :heavy_check_mark: | :heavy_plus_sign: | | :heavy_check_mark: |
|**IR conversion (SSA)** | :heavy_multiplication_x: | :heavy_plus_sign: | :heavy_plus_sign: | :heavy_multiplication_x: | | :heavy_plus_sign: |
|**Symbolic Execution** | :heavy_multiplication_x: | :heavy_plus_sign: | :heavy_plus_sign: | :heavy_multiplication_x: | | :heavy_plus_sign: |

* IDA plugin :heavy_plus_sign:
* Binary ninja plugin :heavy_plus_sign:
* Pypi package :heavy_plus_sign:

:heavy_check_mark: **DONE** / :heavy_plus_sign: **WIP** / :heavy_multiplication_x: **TODO** / :o: **N/A**


## Requirements

Octopus is supported on Linux (ideally Ubuntu 16.04) and requires Python >=3.3 (ideally 3.6).

Dependencies:
* Graph generation: [graphviz](https://graphviz.gitlab.io/download/)
* Explorer: [requests](http://docs.python-requests.org/en/master/#)
* Symbolic Execution: [z3-solver](https://pypi.org/project/z3-solver/)
* Wasm: [wasm](https://github.com/athre0z/wasm)

## Quick Start

Install Octopus easily with:

```
# Install system dependencies
sudo apt-get update && sudo apt-get install python-pip graphviz -y

# Download Octopus
git clone https://github.com/quoscient/octopus
cd octopus

# Install Octopus and its dependencies
pip3 install -r requirements.txt

# Run tests for all platforms (disassembly, CFG, ...)
./run_tests.sh
# Run tests that require internet access (explorer tests)
./run_explorer_tests.sh

# Run tests for only one platforms
# {btc, eth, eos, neo, wasm}_run_tests.sh
cd octopus/tests/
./wasm_run_tests.sh
```

## Examples

<details><summary>WebAssembly</summary>
<p>

#### Disassembler

Disassembly of a Wasm module:
```python
from octopus.arch.wasm.disassembler import WasmDisassembler

FILE = "examples/wasm/samples/helloworld.wasm"

with open(FILE, 'rb') as f:
    module_bytecode = f.read()

# return list of functions instructions (list)
print(disasm.disassemble_module(module_bytecode))
#[[<octopus.arch.wasm.instruction.WasmInstruction at 0x7f85e4904278>,<octopus.arch.wasm.instruction.WasmInstruction at 0x7f85e4904f60>,<octopus.arch.wasm.instruction.WasmInstruction at 0x7f85e4904ef0>]]

# return text of functions code
print(disasm.disassemble_module(module_bytecode, r_format='text'))
# func 0
# i32.const 0
# call 0
# end
```

Disassembly of wasm bytecode:
```python
from octopus.arch.wasm.disassembler import WasmDisassembler

# bytecode in WebAssembly is the function code (i.e. function body)
bytecode = b'\x02\x7fA\x18\x10\x1cA\x00\x0f\x0b'
# create a WasmDisassembler object
disasm = WasmDisassembler(bytecode)

# disassemble bytecode into a list of WasmInstruction
# attributes r_format='list' by default
print(disasm.disassemble())

#[<octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904eb8>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904278>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904390>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904ef0>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904f60>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4901048>]

print(disasm.disassemble(r_format='reverse'))

#{0: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4901048>, 1: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904240>, 2: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904f60>, 3: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904ef0>, 4: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904278>, 5: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904390>}

print(disasm.disassemble(r_format='text'))
# block -1
# i32.const 24
# call 28
# i32.const 0
# return
# end
```

#### ModuleAnalyzer

```python
from octopus.arch.wasm.analyzer import WasmModuleAnalyzer

FILE = "examples/wasm/samples/helloworld.wasm"

with open(FILE, 'rb') as f:
    module_bytecode = f.read()

# return list of functions instructions (list)
# attributes analysis=True by default
analyzer = WasmModuleAnalyzer(module_bytecode)

# show analyzer attributes
print(analyzer.show())
# {'datas': [{'data': b'Hello, world\x00',
#    'index': 0,
#    'offset': None,
#    'size': 13}],
#  'elements': [],
#  'exports': [{'field_str': 'memory', 'index': 0, 'kind': 2},
#   {'field_str': 'main', 'index': 1, 'kind': 0}],
#  'func_types': [1],
#  'globals': [],
#  'imports_all': [(0, 'sys', 'print', 0)],
#  'imports_func': [('sys', 'print', 0)],
#  'length codes': 1,
#  'magic': b'\x00asm',
#  'memories': [{'limits_flags': 1,
#    'limits_initial': 200,
#    'limits_maximum': 200}],
#  'start': None,
#  'tables': [],
#  'types': [('i32', ''), ('', '')],
#  'version': b'\x01\x00\x00\x00'}
```

#### Control Flow Analysis

```python
from octopus.arch.wasm.cfg import WasmCFG
from octopus.analysis.graph import CFGGraph

# complete wasm module
file_name = "examples/wasm/samples/fib.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = WasmCFG(raw)

# visualize CFGGraph 
# generate graph.dot and graph.pdf file
graph = CFGGraph(cfg)
graph.view_functions()
```


#### Call Flow Analysis

```python
from octopus.platforms.wasm.cfg import WasmCFG

# fibonacci wasm module
file_name = "examples/wasm/samples/fib.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = WasmCFG(raw)

# visualize Call Flow Graph
# generate call_graph.dot and call_graph.pdf file
# 
# color similar to https://webassembly.studio/
# imported func == turquoise / exported func == grey
# edge label = number of different calls to the function
cfg.visualize_call_flow()
```

</p>
</details>

<details><summary>Ethereum (ETH)</summary>
<p>

#### Explorer

```python
# TODO
```

#### Disassembler

```python
# TODO
```

#### Control Flow Analysis

```python
# TODO
```

#### IR conversion (SSA)

```python
# TODO
```
</p>
</details>

<details><summary>NEO</summary>
<p>

#### Explorer

```python
# TODO
```

#### Disassembler

```python
# TODO
```

#### Control Flow Analysis

```python
# TODO
```

</p>
</details>

<details><summary>EOS</summary>
<p>

#### Explorer

```python
# TODO
```

#### Disassembler


code:
```python
# TODO
```

#### ModuleAnalyzer

```python
# TODO
```

#### Control Flow Analysis

```python
# TODO
```


#### Call Flow Analysis

```python
# TODO
```

</p>
</details>

<details><summary>Bitcoin</summary>
<p>

#### Explorer

```python
# TODO
```

#### Disassembler

code:
```python
# TODO
```

</p>
</details>


Please find other examples in [examples](examples) folder.

## Publications and Videos

* REcon Montreal 2018: [Reverse Engineering Of Blockchain Smart Contracts](https://recon.cx/2018/montreal/schedule/system/event_attachments/attachments/000/000/053/original/RECON-MTL-2018-Reversing_blockchains_smart_contracts.pdf)

## Authors

* **Patrick Ventuzelo** - *Creator* - [@Pat_Ventuzelo](https://twitter.com/pat_ventuzelo)

See also the list of [contributors](https://github.com/quoscient/octopus/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

Inspired by:
* [Manticore](https://github.com/trailofbits/manticore)
* [Mythril](https://github.com/ConsenSys/mythril)
* ...