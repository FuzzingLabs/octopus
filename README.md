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

Octopus support the following types of programs/smart contracts:

* WebAssembly module (WASM)

* Bitcoin script (BTC script)
* Ethereum smart contracts (EVM bytecode)
* EOS smart contracts (WASM)
* NEO smart contracts (AVM bytecode)


## Platforms / Architectures

|| BTC | ETH | EOS | NEO || WASM
|:--------------------:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Explorer** | :heavy_check_mark: | :heavy_check_mark:| :heavy_check_mark: | :heavy_check_mark: | |  :heavy_check_mark: |
|**Disassembler** | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | :heavy_check_mark: |
|**Control Flow Analysis** | :x: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | | :heavy_check_mark: |
|**Call Flow Analysis** | :x: | :heavy_plus_sign: | :heavy_check_mark: | :heavy_plus_sign: | | :heavy_check_mark: |
|**IR conversion (SSA)** | :x: | :heavy_plus_sign: | :heavy_plus_sign: | :x: | | :heavy_plus_sign: |
|**Symbolic Execution** | :x: | :heavy_plus_sign: | :heavy_plus_sign: | :x: | | :heavy_plus_sign: |

* DONE :heavy_check_mark: 
* WIP (Work In Progress) :heavy_plus_sign: 
* NOT PLANNED :x: 

Other: IDA plugin :heavy_plus_sign:, Binary ninja plugin :heavy_plus_sign:, Pypi package :heavy_plus_sign:

## Requirements

Octopus is supported on Linux (ideally Ubuntu 16.04) and requires Python >= 3.0 (ideally 3.6).

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

Please find examples in [examples](examples)

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