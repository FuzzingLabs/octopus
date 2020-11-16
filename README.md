# Octopus

<p align="center">
	<img src="/images/logo-medium.png" height="300px"/>
</p>

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Huge thanks to [QuoScient](https://www.quoscient.io/) for having sponsored this project.

**Octopus is a security analysis framework for WebAssembly module and Blockchain Smart Contract.**

The purpose of Octopus is to provide an easy way to analyze closed-source WebAssembly module and smart contracts bytecode to understand deeper their internal behaviours.


## Features

- **Explorer**: Octopus JSON-RPC client implementation to communicate with blockchain platforms
- **Disassembler**: Octopus can translate bytecode into assembly representation
- **Control Flow Analysis**: Octopus can generate a Control Flow Graph (CFG) 
- **Call Flow Analysis**: Octopus can generate a Call Flow Graph (function level) 
- **IR conversion (SSA)**: Octopus can simplify assembly into Static Single Assignment (SSA) representation
- **Symbolic Execution**: Octopus use symbolic execution to find new paths into a program

## Platforms / Architectures

Octopus support the following types of programs/smart contracts:
* WebAssembly module (WASM)
* Bitcoin script (BTC script)
* Ethereum smart contracts (EVM bytecode & Ewasm)
* EOS smart contracts (WASM)
* NEO smart contracts (AVM bytecode)


|| BTC | ETH (EVM) | ETH (WASM) | EOS | NEO || WASM |
|:--------------------:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Explorer** | :heavy_check_mark: | :heavy_check_mark:| :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | :o: |
|**Disassembler** | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | :heavy_check_mark: |
|**Control Flow Analysis** | :heavy_multiplication_x: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | :heavy_check_mark: |
|**Call Flow Analysis** | :heavy_multiplication_x: | :heavy_plus_sign: | :heavy_check_mark: | :heavy_check_mark: | :heavy_plus_sign: | | :heavy_check_mark: |
|**IR conversion (SSA)** | :heavy_multiplication_x: | :heavy_check_mark: | :heavy_plus_sign: | :heavy_plus_sign: | :heavy_multiplication_x: | | :heavy_check_mark: |
|**Symbolic Execution** | :heavy_multiplication_x: | :heavy_plus_sign: | :heavy_plus_sign: | :heavy_plus_sign: | :heavy_multiplication_x: | | :heavy_plus_sign: |


* PyPI package :heavy_check_mark:
* Docker :heavy_check_mark:

:heavy_check_mark: **DONE** / :heavy_plus_sign: **WIP** / :heavy_multiplication_x: **TODO** / :o: **N/A**


## Requirements

Octopus is supported on Linux (ideally Ubuntu 16.04) and requires Python >=3.5 (ideally 3.6).

Dependencies:
* Graph generation: [graphviz](https://graphviz.gitlab.io/download/)
* Explorer: [requests](http://docs.python-requests.org/en/master/#)
* Symbolic Execution: [z3-solver](https://pypi.org/project/z3-solver/)
* Wasm: [wasm](https://github.com/athre0z/wasm)

## Quick Start

- Install system dependencies
```
# Install system dependencies
sudo apt-get update && sudo apt-get install python-pip graphviz xdg-utils -y
```

- Install Octopus:
```
# Download Octopus
git clone https://github.com/pventuzelo/octopus
cd octopus

# Install Octopus library/CLI and its dependencies
python3 setup.py install
```
or
```
# but prefer the first way to install if possible
pip3 install octopus
```

- Run tests
```
# Run tests for all platforms (disassembly, CFG, ...)
./run_tests.sh
# Run tests that require internet access (explorer tests)
./run_explorer_tests.sh

# Run tests for only one platforms
# {btc, eth, eos, neo, wasm}_run_tests.sh
cd octopus/tests/
./wasm_run_tests.sh
```

#### Docker container

A docker container providing the toolset is available at [docker hub](https://hub.docker.com/r/smartbugs/octopus). 
In a terminal, run the following commands:

```
docker pull smartbugs/octopus
docker run -it smartbugs/octopus
cd octopus
python3 octopus_eth_evm.py -s -f examples/ETH/evm_bytecode/61EDCDf5bb737ADffE5043706e7C5bb1f1a56eEA.bytecode
```

## Command-line tools

* WebAssembly: [octopus_wasm.py](octopus_wasm.py)
* Ethereum (EVM): [octopus_eth_evm.py](octopus_eth_evm.py)


## In-depth Examples using APIs

<details><summary>WebAssembly</summary>
<p>

#### Disassembler

Disassembly of a Wasm module:
```python
from octopus.arch.wasm.disassembler import WasmDisassembler

FILE = "examples/wasm/samples/helloworld.wasm"

with open(FILE, 'rb') as f:
    module_bytecode = f.read()

disasm = WasmDisassembler()
# return list of functions instructions (list)
print(disasm.disassemble_module(module_bytecode))
#[[<octopus.arch.wasm.instruction.WasmInstruction at 0x7f85e4904278>,<octopus.arch.wasm.instruction.WasmInstruction at 0x7f85e4904f60>,<octopus.arch.wasm.instruction.WasmInstruction at 0x7f85e4904ef0>]]

print()
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
print()
print(disasm.disassemble(r_format='reverse'))

#{0: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4901048>, 1: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904240>, 2: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904f60>, 3: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904ef0>, 4: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904278>, 5: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904390>}
print()
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

FILE = "examples/wasm/samples/hello_wasm_studio.wasm"

with open(FILE, 'rb') as f:
    module_bytecode = f.read()

# return list of functions instructions (list)
# attributes analysis=True by default
analyzer = WasmModuleAnalyzer(module_bytecode)

# show analyzer attributes
print(analyzer.func_prototypes)
# [('putc_js', 'i32', ''),
#  ('__syscall0', 'i32', 'i32'),
#  ('__syscall3', 'i32 i32 i32 i32', 'i32'),
#  ('__syscall1', 'i32 i32', 'i32'),
#  ('__syscall5', 'i32 i32 i32 i32 i32 i32', 'i32'),
#  ('__syscall4', 'i32 i32 i32 i32 i32', 'i32'),
#  ('$func6', '', ''),
#  ('main', '', 'i32'),
#  ('writev_c', 'i32 i32 i32', 'i32'),
#  ('$func9', '', 'i32'),
#  ('$func10', 'i32', 'i32'),
#  ('$func11', 'i32', 'i32'),
#  ('$func12', 'i32', ''),
#  ('$func13', 'i32', 'i32'),
#  ('$func14', 'i32 i32 i32 i32', 'i32'),
#  ('$func15', 'i32 i32', 'i32'),
#  ('$func16', 'i32 i32', 'i32'),
#  ('$func17', 'i32', 'i32'),
#  ('$func18', 'i32', 'i32'),
#  ('$func19', 'i32', 'i32'),
#  ('$func20', 'i32 i32 i32', 'i32'),
#  ('$func21', 'i32 i32 i32', 'i32'),
#  ('$func22', 'i32 i64 i32', 'i64'),
#  ('$func23', 'i32 i32 i32', 'i32'),
#  ('$func24', 'i32', 'i32'),
#  ('$func25', 'i32 i32 i32 i32', '')]
print()
print(analyzer.contains_emscripten_syscalls())
#[('__syscall0', 'restart_syscall'),
# ('__syscall3', 'read'),
# ('__syscall1', 'exit'),
# ('__syscall5', 'open'),
# ('__syscall4', 'write')]
```

#### Control Flow Analysis

```python
from octopus.arch.wasm.cfg import WasmCFG

# complete wasm module
file_name = "examples/wasm/samples/fib.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = WasmCFG(raw)

# visualize CFGGraph 
# generate graph.dot and graph.pdf file
cfg.visualize()
```

<p align="center">
    <img src="/images/wasm-cfg-fib.png" height="400px"/>
</p>


#### Functions' instructions analytics

```python
from octopus.arch.wasm.cfg import WasmCFG

# complete wasm module
file_name = "examples/wasm/samples/hello_wasm_studio.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = WasmCFG(raw)

# visualization
cfg.visualize_instrs_per_funcs()
```

<p align="center">
    <img src="/images/wasm-instr-func-analytics.png" height="400px"/>
</p>

#### Call Flow Analysis

```python
from octopus.arch.wasm.cfg import WasmCFG

# fibonacci wasm module
file_name = "examples/wasm/samples/hello_wasm_studio.wasm"

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

<p align="center">
    <img src="/images/wasm-callflow-hello-studio.png" height="400px"/>
</p>

Legend:  

<p align="center">
    <img src="/images/legend_callgraph.png" height="400px"/>
</p>

#### IR conversion (SSA)

```python
from octopus.arch.wasm.emulator import WasmSSAEmulatorEngine

# complete wasm module
file_name = "examples/wasm/samples/fib.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()


# run the emulator for SSA
emul = WasmSSAEmulatorEngine(raw)
emul.emulate_one_function('fib')
# or emul.emulate_functions(['fib'])
# or emul.emulate_functions() # emulate all the function

# visualization of the cfg with SSA
emul.cfg.visualize(ssa=True)
```

<p align="center">
    <img src="/images/ssa-cfg-fib-wasm.png" height="400px"/>
</p>


</p>
</details>

<details><summary>Ethereum (ETH) - EVM</summary>
<p>

#### Explorer

```python
from octopus.platforms.ETH.explorer import EthereumInfuraExplorer
from octopus.platforms.ETH.explorer import INFURA_ROPSTEN

KEY_API = "bHuaQhX91nkQBac8Wtgj"
# connection to ROPSTEN network (testnet)
explorer = EthereumInfuraExplorer(KEY_API, network=INFURA_ROPSTEN)

# connection to MAINNET network (mainnet)
# explorer = EthereumInfuraExplorer(KEY_API)

# Test ROPSTEN network current block number
block_number = explorer.eth_blockNumber()
print(block_number)
# 3675552

# Retrieve code of this smart contract
addr = "0x3c6B10a5239B1a8A27398583F49771485382818F"
code = explorer.eth_getCode(addr)
print(code)
# 0x6060604052600436106049576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806360fe47b114604e5780636d4ce63c14606e575b600080fd5b3415605857600080fd5b606c60048080359060200190919050506094565b005b3415607857600080fd5b607e609e565b6040518082815260200191505060405180910390f35b8060008190555050565b600080549050905600a165627a7a72305820e1f98c821c12eea52047d7324b034ddccc41eaa7365d369b34580ab73c71a8940029
```

#### Disassembler

```python
from octopus.platforms.ETH.disassembler import EthereumDisassembler

# smart contract bytecode
bytecode_hex = "60606040526000357c0100000000000000000000000000000000000000000000000000000000900480635fd8c7101461004f578063c0e317fb1461005e578063f8b2cb4f1461006d5761004d565b005b61005c6004805050610099565b005b61006b600480505061013e565b005b610083600480803590602001909190505061017d565b6040518082815260200191505060405180910390f35b3373ffffffffffffffffffffffffffffffffffffffff16611111600060005060003373ffffffffffffffffffffffffffffffffffffffff16815260200190815260200160002060005054604051809050600060405180830381858888f19350505050151561010657610002565b6000600060005060003373ffffffffffffffffffffffffffffffffffffffff168152602001908152602001600020600050819055505b565b34600060005060003373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000828282505401925050819055505b565b6000600060005060008373ffffffffffffffffffffffffffffffffffffffff1681526020019081526020016000206000505490506101b6565b91905056"

disasm = EthereumDisassembler()
disasm.disassemble(bytecode_hex)

# disassemble bytecode into a list of EthereumInstruction
# attributes r_format='list' by default
print(disasm.disassemble(bytecode_hex))

#[<octopus.platforms.ETH.instruction.EthereumInstruction object at 0x7f85d4add5c0>, <octopus.platforms.ETH.instruction.EthereumInstruction object at 0x7f85d4ad8588>, <octopus.platforms.ETH.instruction.EthereumInstruction object at 0x7f85d4ad8c50>]

print()
print(disasm.disassemble(bytecode_hex, r_format='reverse'))

# {0: <octopus.platforms.ETH.instruction.EthereumInstruction object at 0x7f85d4ad8160>, ..., 229: <octopus.platforms.ETH.instruction.EthereumInstruction object at 0x7f85d4ad8630>, 230: <octopus.platforms.ETH.instruction.EthereumInstruction object at 0x7f85d4ad87b8>}

print()
print(disasm.disassemble(bytecode_hex,r_format='text'))
# PUSH1 0x60
# PUSH1 0x40
# MSTORE
# PUSH1 0x0
# CALLDATALOAD
# PUSH29 0x100000000000000000000000000000000000000000000000000000000
# SWAP1
# DIV
# DUP1
# PUSH4 0x5fd8c710
# EQ
# PUSH2 0x4f
# JUMPI
# ...
# SWAP2
# SWAP1
# POP
# JUMP
```

#### Control Flow Analysis

```python
from octopus.analysis.graph import CFGGraph
from octopus.platforms.ETH.cfg import EthereumCFG

# ethernaut0 bytecode
file_name = "examples/ETH/evm_bytecode/Zeppelin_Hello_ethernaut0.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex)


# generic visualization api
# generate graph.dot and graph.pdf file
graph = CFGGraph(cfg)
graph.view()
# or directly using the cfg binding
# cfg.visualize()
# and you can get a simplify cfg representation using
# cfg.visualize(simplify=True) or graph.view(simplify=True)
```

<p align="center">
    <img src="/images/eth-cfg-evm.png"/>
</p>

#### IR conversion (SSA)

```python
# The conversion to SSA is already done by the SSAEmulator
# when the CFG is reconstruct
# by default you have just to visualize it
from octopus.platforms.ETH.cfg import EthereumCFG

# ethernaut0 bytecode
file_name = "examples/ETH/evm_bytecode/Zeppelin_Hello_ethernaut0.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex)

# SSA visualization
cfg.visualize(ssa=True)
```

<p align="center">
    <img src="/images/eth-cfg-evm-ssa.png"/>
</p>


</p>
</details>

<details><summary>Ethereum (WASM)</summary>
<p>

#### Explorer

```python
from octopus.platforms.ETH.explorer import EthereumInfuraExplorer
from octopus.platforms.ETH.explorer import INFURA_KOVAN

# connection to ROPSTEN network (testnet)
explorer = EthereumInfuraExplorer("bHuaQhX91nkQBac8Wtgj",
                                  network=INFURA_KOVAN)
# connection to MAINNET network (mainnet)
# explorer = EthereumInfuraExplorer("bHuaQhX91nkQBac8Wtgj")

# test infura access
block_number = explorer.eth_blockNumber()
print('blockNumber = %d' % block_number)

# retrieve code of this smart contract
addr = "0x1120e596b173d953ba52ce262f73ce3734b0e40e"
code = explorer.eth_getCode(addr)
print()
print(code)
# blockNumber = 8803487
# 
# 0x0061736d0100000001090260000060027f7f00021a0203656e7603726574000103656e76066d656d6f7279020102100303020000040501700101010501000601000708010463616c6c00010a120205001002000b0a00418008410b1000000b0b1201004180080b0b48656c6c6f20776f726c64000b076c696e6b696e6703010b0066046e616d65015f060003726574010570616e6963020463616c6c032f5f5a4e3134707761736d5f657468657265756d3365787433726574313768363034643830393864313638366338304504066465706c6f790511727573745f626567696e5f756e77696e64
```

#### Disassembler

Disassembly of a Wasm module:
```python
from octopus.platforms.ETH.disassembler import EthereumDisassembler

FILE = "examples/ETH/wasm/helloworld_kovan.bytecode"

with open(FILE, 'r') as f:
    module_bytecode = f.read()

disasm = EthereumDisassembler(arch='wasm')
# return list of functions instructions (list)
print(disasm.disassemble_module(module_bytecode))
#[[<octopus.arch.wasm.instruction.WasmInstruction object at 0x7efc0ceaa898>], [<octopus.arch.wasm.instruction.WasmInstruction object at 0x7efc0ceaa7b8>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7efc0ceaa780>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7efc0ceaa748>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7efc0ceaa6d8>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7efc0ceaa710>]]

print()
# return text of functions code
print(disasm.disassemble_module(module_bytecode, r_format='text'))
# func 0
# end
# 
# func 1
# call 1
# i32.const 1036
# i32.const 232
# call 0
# end

```

Disassembly of wasm bytecode:
```python
from octopus.platforms.ETH.disassembler import EthereumDisassembler

# bytecode in WebAssembly is the function code (i.e. function body)
bytecode = b'\x02\x7fA\x18\x10\x1cA\x00\x0f\x0b'
# create a WasmDisassembler object
disasm = EthereumDisassembler(bytecode, arch='wasm')

# disassemble bytecode into a list of WasmInstruction
# attributes r_format='list' by default
print(disasm.disassemble())

#[<octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904eb8>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904278>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904390>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904ef0>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904f60>, <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4901048>]
print()
print(disasm.disassemble(r_format='reverse'))

#{0: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4901048>, 1: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904240>, 2: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904f60>, 3: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904ef0>, 4: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904278>, 5: <octopus.arch.wasm.instruction.WasmInstruction object at 0x7f85e4904390>}
print()
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

FILE = "examples/ETH/wasm/helloworld_kovan.bytecode"

with open(FILE, 'r') as f:
    module_bytecode = f.read()

# return list of functions instructions (list)
# attributes analysis=True by default
analyzer = WasmModuleAnalyzer(module_bytecode)

# show analyzer attributes
print(analyzer.func_prototypes)
# [('ret', 'i32 i32', '', 'import'), ('$func1', '', '', 'local'), ('call', '', '', 'export')]
print()
print(analyzer.exports)
# [{'field_str': 'call', 'kind': 0, 'index': 2}]
print()
print(analyzer.imports_func)
# [('env', 'ret', 1)]
print()
print(analyzer.datas)
# [{'data': b'Hello world', 'index': 0, 'offset': None, 'size': 11},
# {'data': b'\x00asm\x01\x00\x00\x00\x01\t\x02`\x00\x00`\x02\x7f\x7f\x00\x02\x1a\x02\x03env\x03ret\x00\x01\x03env\x06memory\x02\x01\x02\x10\x03\x03\x02\x00\x00\x04\x05\x01p\x01\x01\x01\x05\x01\x00\x06\x01\x00\x07\x08\x01\x04call\x00\x01\n\x12\x02\x05\x00\x10\x02\x00\x0b\n\x00A\x80\x08A\x0b\x10\x00\x00\x0b\x0b\x12\x01\x00A\x80\x08\x0b\x0bHello world\x00\x0b\x07linking\x03\x01\x0b\x00f\x04name\x01_\x06\x00\x03ret\x01\x05panic\x02\x04call\x03/_ZN14pwasm_ethereum3ext3ret17h604d8098d1686c80E\x04\x06deploy\x05\x11rust_begin_unwind',
# 'index': 0,
# 'offset': None,
# 'size': 232}]

```

#### Control Flow Analysis

```python
from octopus.platforms.ETH.cfg import EthereumCFG

# HelloWorld on Kovan Parity Network
file_name = "examples/ETH/wasm/helloworld_kovan.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex, arch='wasm')
cfg.visualize()
```

<p align="center">
    <img src="/images/eth-wasm-cfg-hello-parity.png" height="400px"/>
</p>

#### Functions' instructions analytics

```python
from octopus.platforms.ETH.cfg import EthereumCFG

# HelloWorld on Kovan Parity Network
file_name = "examples/ETH/wasm/helloworld_kovan.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex, arch='wasm')

# visualization
cfg.visualize_instrs_per_funcs()
```

<p align="center">
    <img src="/images/eth-wasm-func-analytics.png" height="400px"/>
</p>

#### Call Flow Analysis

```python
from octopus.platforms.ETH.cfg import EthereumCFG

# HelloWorld on Kovan Parity Network
file_name = "examples/ETH/wasm/helloworld_kovan.bytecode"

# read file
with open(file_name) as f:
    bytecode_hex = f.read()

# create the CFG
cfg = EthereumCFG(bytecode_hex, arch='wasm')

# visualization
cfg.visualize_call_flow()
```

<p align="center">
    <img src="/images/eth-wasm-callflow-hello-parity.png" height="400px"/>
</p>

Legend:  

<p align="center">
    <img src="/images/legend_callgraph.png" height="400px"/>
</p>


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
from octopus.platforms.NEO.explorer import NeoExplorerRPC

# get list nodes here: http://monitor.cityofzion.io/
explorer = NeoExplorerRPC(host='seed2.neo.org')

# get current number of block on the blockchain
print(explorer.getblockcount())
# 2534868

# get information on a contract
# lock smart contract address: d3cce84d0800172d09c88ccad61130611bd047a4
contract = explorer.getcontractstate("d3cce84d0800172d09c88ccad61130611bd047a4")
print(contract)
# {'author': 'Erik Zhang',
# 'code_version': '2.0',
# 'description': 'Lock 2.0',
# 'email': 'erik@neo.org',
# 'hash': '0xd3cce84d0800172d09c88ccad61130611bd047a4',
# 'name': 'Lock',
# 'parameters': ['Integer', 'PublicKey', 'Signature'],
# 'properties': {'dynamic_invoke': False, 'storage': False},
# 'returntype': 'Boolean',
# 'script': '56c56b6c766b00527ac46c766b51527ac46c766b52527ac4616168184e656f2e426c6f636b636861696e2e4765744865696768746168184e656f2e426c6f636b636861696e2e4765744865616465726c766b53527ac46c766b00c36c766b53c36168174e656f2e4865616465722e47657454696d657374616d70a06c766b54527ac46c766b54c3640e00006c766b55527ac4621a006c766b51c36c766b52c3617cac6c766b55527ac46203006c766b55c3616c7566',
# 'version': 0}

# smart contract code in contract['script']
print(contract['script'])
```

#### Disassembler

```python
from octopus.platforms.NEO.disassembler import NeoDisassembler

# lock contract
file_name = "examples/NEO/samples/Lock.bytecode"

# read file
with open(file_name) as f:
    bytecode = f.read()

disasm = NeoDisassembler()

print(disasm.disassemble(bytecode, r_format='text'))
# PUSH6
# NEWARRAY
# TOALTSTACK
# FROMALTSTACK
# DUP
# TOALTSTACK
# PUSH0
# PUSH2
# ROLL
# SETITEM
# FROMALTSTACK
# ....
# PICKITEM
# NOP
# FROMALTSTACK
# DROP
# RET
```

#### Control Flow Analysis

```python
from octopus.analysis.graph import CFGGraph
from octopus.platforms.NEO.cfg import NeoCFG

# lock contract
file_name = "examples/NEO/samples/Lock.bytecode"

# read file
with open(file_name) as f:
    raw = f.read()

# create neo cfg - automatic static analysis
cfg = NeoCFG(raw)

# graph visualization
graph = CFGGraph(cfg, filename="Lock_cfg")
graph.view_functions()
```

<p align="center">
    <img src="/images/neo-cfg.png"/>
</p>


</p>
</details>

<details><summary>EOS</summary>
<p>

#### Explorer

```python
from octopus.platforms.EOS.explorer import EosExplorer

host = "api.cypherglass.com"

# by defaul the port is 8888
explo = EosExplorer(host=host)

# get info about the node
explo.get_info()

'''
{'block_cpu_limit': 180289,
 'block_net_limit': 1045680,
 'chain_id': 'aca376f206b8fc25a6ed44dbdc66547c36c6c33e3a119ffbeaef943642f0e906',
 'head_block_id': '018d6e2bcf6295126cd74cf694b5cca3529eefc42b334b394ef87c3a43876739',
 'head_block_num': 26045995,
 'head_block_producer': 'eosswedenorg',
 'head_block_time': '2018-11-09T14:11:29.500',
 'last_irreversible_block_id': '018d6cdcff78bbd9f25c605b02fb67c47a337ece78ddcf73089cee4bf6a410ee',
 'last_irreversible_block_num': 26045660,
 'server_version': 'c71d2245',
 'server_version_string': 'mainnet-1.3.0',
 'virtual_block_cpu_limit': 38092879,
 'virtual_block_net_limit': 1048576000}
'''
explo.get_block(1337)

'''
{'action_mroot': 'bcb9763baa3bbf98ed36379b4be0ecb2d9cd21c75df01729c63b2b021001c10c',
 'block_extensions': [],
 'block_num': 1337,
 'confirmed': 0,
 'header_extensions': [],
 'id': '00000539d17a03af7126e073be4c4d99a72b7f58793cf2c87b9bfd41b6c711fb',
 'new_producers': None,
 'previous': '00000538b374c1cbfaeed7253ad3075ddc72a28f0a0515301fc1bbed675f2316',
 'producer': 'eosio',
 'producer_signature': 'SIG_K1_K5jWf36t6j454Hb2fGuV37YTwMTvuQ51ZPBtpru8Ud2axtMTEauWyvtpJuTpnvqzReUndDgEDXvoeEP4jdj2bpnYKBt6g2',
 'ref_block_prefix': 1944069745,
 'schedule_version': 0,
 'timestamp': '2018-06-09T12:09:21.500',
 'transaction_mroot': '0000000000000000000000000000000000000000000000000000000000000000',
 'transactions': []}
'''
```

#### Disassembler

```python
from octopus.platforms.EOS.disassembler import EosDisassembler

# complete wasm module
file_name = "examples/EOS/samples/eos_ping.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# just disassembly
disasm = EosDisassembler()

# because we provide full module bytecode
# we need to use disassemble_module()
# otherwise just disassemble() is enough
text = disasm.disassemble_module(raw, r_format="text")
print(text)
# func 0
# get_local 0
# get_local 1
# i32.const 32
# call 12
# i32.eqz
# end
# 
# func 1
# get_local 0
# i64.load 3, 0
# get_local 0
# i64.load 3, 8
# call 6
# end
# 
# func 2
# ...
# end
# 
# ...
```

#### ModuleAnalyzer

```python

from octopus.platforms.EOS.analyzer import EosAnalyzer

# complete wasm module
file_name = "examples/EOS/samples/eos_ping.wasm"

with open(file_name, 'rb') as f:
    module_bytecode = f.read()

# return list of functions instructions (list)
# attributes analysis=True by default
analyzer = EosAnalyzer(module_bytecode)

# show analyzer attributes
print(analyzer.func_prototypes)
#[('action_data_size', '', 'i32', 'import'), ('eosio_assert', 'i32 i32', '', 'import'), ('eosio_exit', 'i32', '', 'import'), ('memcpy', 'i32 i32 i32', 'i32', 'import'), ('prints', 'i32', '', 'import'), ('read_action_data', 'i32 i32', 'i32', 'import'), ('require_auth2', 'i64 i64', '', 'import'), ('_ZeqRK11checksum256S1_', 'i32 i32', 'i32', 'export'), ('_ZN5eosio12require_authERKNS_16permission_levelE', 'i32', '', 'export'), ('apply', 'i64 i64 i64', '', 'export'), ('$func10', 'i32 i64', '', 'local'), ('$func11', 'i32 i32', 'i32', 'local'), ('memcmp', 'i32 i32 i32', 'i32', 'export'), ('malloc', 'i32', 'i32', 'export'), ('$func14', 'i32 i32', 'i32', 'local'), ('$func15', 'i32', 'i32', 'local'), ('free', 'i32', '', 'export'), ('$func17', '', '', 'local')]
print()
print(analyzer.exports)
# [{'field_str': 'memory', 'kind': 2, 'index': 0}, {'field_str': '_ZeqRK11checksum256S1_', 'kind': 0, 'index': 7}, {'field_str': '_ZN5eosio12require_authERKNS_16permission_levelE', 'kind': 0, 'index': 8}, {'field_str': 'apply', 'kind': 0, 'index': 9}, {'field_str': 'memcmp', 'kind': 0, 'index': 12}, {'field_str': 'malloc', 'kind': 0, 'index': 13}, {'field_str': 'free', 'kind': 0, 'index': 16}]
print()
print(analyzer.imports_func)
# [('env', 'action_data_size', 3), ('env', 'eosio_assert', 5), ('env', 'eosio_exit', 2), ('env', 'memcpy', 6), ('env', 'prints', 2), ('env', 'read_action_data', 4), ('env', 'require_auth2', 1)]
```

#### Control Flow Analysis

```python
from octopus.platforms.EOS.cfg import EosCFG
from octopus.analysis.graph import CFGGraph

# complete wasm module
file_name = "examples/EOS/samples/eos_ping.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = EosCFG(raw)

# visualize
graph = CFGGraph(cfg)
graph.view_functions()
```


<p align="center">
    <img src="/images/eos-cfg.png"/>
</p>

#### Call Flow Analysis

```python
from octopus.platforms.EOS.cfg import EosCFG

# complete wasm module
file_name = "examples/EOS/samples/eos_ping.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = EosCFG(raw)

# visualize
cfg.visualize_call_flow()
```

<p align="center">
    <img src="/images/eos-callgraph.png"/>
</p>

#### Functions' instructions analytics

```python
from octopus.platforms.EOS.cfg import EosCFG

# complete wasm module
file_name = "examples/EOS/samples/eos_ping.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()

# create the cfg
cfg = EosCFG(raw)

# visualize
cfg.visualize_instrs_per_funcs()
```

<p align="center">
    <img src="/images/eos-func-instrucs.png"/>
</p>

</p>
</details>

<details><summary>Bitcoin</summary>
<p>

#### Explorer

```python
from octopus.platforms.BTC.explorer import BitcoinExplorerRPC

RPC_USER = 'test'
RPC_PASSWORD = 'test'
RPC_HOST = 'localhost'

host = '%s:%s@%s' % (RPC_USER, RPC_PASSWORD, RPC_HOST)

explorer = BitcoinExplorerRPC(host)

explorer.getbestblockhash()
# '00000000000000000012085cfe8c79bcdacf81fbd82f6ab52c3cb3a454d4987c'

explorer.getblockcount()
#550859
```

#### Disassembler

```python
from octopus.platforms.BTC.disassembler import BitcoinDisassembler

# Witness Script
file_name = "examples/BTC/witness_script.hex"

# read file
with open(file_name) as f:
    bytecode = f.read()

disasm = BitcoinDisassembler()

print(disasm.disassemble(bytecode, r_format='text'))
# 0
# OP_ROT
# OP_ROT
# 2
# 0203f4d01d0b35588638631ebb7d46d8387fd1aeb3dbecfdd3faf7c056b023c833
# 03aa6677e3ce1bd634f4f2e1cd60a60af002e1b30484d4d1611b183b16d391ee96
# 03bf164811abb8c91ed39e58d4e307f86cb4e487c83f727a2c482bc71a0f96f1db
# 3
# OP_CHECKMULTISIG
```

</p>
</details>


Please find examples in [examples](examples) folder.

## Publications and Videos

* BLACKALPS 2018 [Reversing and Vulnerability research of Ethereum Smart Contracts](https://www.blackalps.ch/ba-18/talks.php#111)
* Devcon iv. [Reversing Ethereum Smart Contracts to find out what's behind EVM bytecode](https://guidebook.com/guide/117233/event/21956134/)
* hack.lu 2018 [Reversing and Vulnerability research of Ethereum Smart Contracts](https://2018.hack.lu/talks/#Reversing+and+Vulnerability+research+of+Ethereum+Smart+Contracts)
* ToorCon XX - 2018 [Reversing Ethereum Smart Contracts (Introduction)](https://frab.toorcon.net/en/toorcon20/public/events/97)
* ToorCon XX - 2018 [Dissection of WebAssembly module](https://frab.toorcon.net/en/toorcon20/public/events/92)
* REcon Montreal 2018: [Reverse Engineering Of Blockchain Smart Contracts](https://recon.cx/2018/montreal/schedule/system/event_attachments/attachments/000/000/053/original/RECON-MTL-2018-Reversing_blockchains_smart_contracts.pdf)

## Authors

**Patrick Ventuzelo** - *Creator* - [@Pat_Ventuzelo](https://twitter.com/pat_ventuzelo)

See also the list of [contributors](https://github.com/quoscient/octopus/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

Sponsor:
* [QuoScient](https://www.quoscient.io/)

Inspired by:
* [Manticore](https://github.com/trailofbits/manticore)
* [Mythril](https://github.com/ConsenSys/mythril)
* [Rattle](https://github.com/trailofbits/rattle)
* [ethersplay](https://github.com/trailofbits/ethersplay)
* ...

# Trainings & Contact

Patrick Ventuzelo - [@pat_ventuzelo](https://twitter.com/pat_ventuzelo)
* Independent Security Researcher / Trainer.
* FREE online courses: [here](https://academy.fuzzinglabs.com/)
