# Octopus
[![Generic badge](https://img.shields.io/badge/REcon-MTL%202018-red.svg)](https://recon.cx/2018/montreal/)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/quoscient/octopus/graphs/commit-activity)
[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<p align="center">
	<img src="/images/logo-medium.png" height="400px"/>
</p>

**Octopus is a security analysis framework for WebAssembly module and Blockchain Smart Contract.**

The purpose of Octopus is to provide an easy way to analyze smart contract security and understand better what is really stored on the blockchain.


## Features

- **Explorer**: Octopus JSON-RPC client implementation to communicate with blockchain platforms
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


* PyPI package :heavy_check_mark:
* IDA plugin :heavy_plus_sign:
* Binary ninja plugin :heavy_plus_sign:

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
sudo apt-get update && sudo apt-get install python-pip graphviz -y
```

- Install Octopus easily with:
```
pip3 install octopus
```
or
```
# Download Octopus
git clone https://github.com/quoscient/octopus
cd octopus

# Install Octopus and its dependencies
pip3 install -r requirements.txt
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

Legend:  `imported` ![#f03c15](https://placehold.it/15/40E0D0/000000?text=+) / ![#c5f015](https://placehold.it/15/808080/000000?text=+) 
`exported` function

</p>
</details>

<details><summary>Ethereum (ETH)</summary>
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
from octopus.platforms.NEO.explorer import NeoExplorerRPC

# get list nodes here: http://monitor.cityofzion.io/
explorer = NeoExplorerRPC(host='pyrpc1.nodeneo.ch')

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

</p>
</details>

<details><summary>EOS</summary>
<p>

#### Explorer

```python
# TODO
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
# TODO
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

</p>
</details>

<details><summary>Bitcoin</summary>
<p>

#### Explorer

```python
# TODO
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

* REcon Montreal 2018: [Reverse Engineering Of Blockchain Smart Contracts](https://recon.cx/2018/montreal/schedule/system/event_attachments/attachments/000/000/053/original/RECON-MTL-2018-Reversing_blockchains_smart_contracts.pdf)

## Authors

* **Patrick Ventuzelo** - *Creator* - [@Pat_Ventuzelo](https://twitter.com/pat_ventuzelo)

See also the list of [contributors](https://github.com/quoscient/octopus/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

Inspired by:
* [Manticore](https://github.com/trailofbits/manticore)
* [Mythril](https://github.com/ConsenSys/mythril)
* ...