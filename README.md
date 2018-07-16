# Octopus

<img src="/images/logo-medium.png" height="400px"/>

README IN PROGRESS

Octopus is a security analysis framework focus on Blockchain Smart Contract. The purpose of Octopus is to provide an easy way to analyze smart contract security and understand better what is really stored on the blockchain.

## Features

### Platforms
* BTC: Explorer, Disassembler
* ETH: Explorer, Disassembler, ControlFlowGraph, SSA (WIP), Symbolic execution (WIP)
* NEO: Explorer, Disassembler, ControlFlowGraph
* EOS: Explorer, Disassembler, ModuleAnalyzer, Callgraph, ControlFlowGraph (WIP)

### Architectures
* WebAssembly: Disassembler, ModuleAnalyzer, Callgraph, ControlFlowGraph (WIP)


* Plugins: IDA (WIP), Binary ninja (WIP)

## Install & Tests

Octopus used Python>3.0 and should work ideally with python>=3.6

```
git clone https://github.com/quoscient/octopus
cd octopus
pip3 install -r requirements.txt
# run tests (disassembly, CFG, ...)
./run_tests.sh
# require internet connectivity (explorer tests)
./run_explorer_tests.sh
```

Pypi package (WIP)

## Publications and Videos

* REcon Montreal 2018: [Reverse Engineering Of Blockchain Smart Contracts](https://recon.cx/2018/montreal/schedule/system/event_attachments/attachments/000/000/053/original/RECON-MTL-2018-Reversing_blockchains_smart_contracts.pdf)

## Examples

Please find examples in ```examples```

## Credits

Inspired by:
* [Manticore](https://github.com/trailofbits/manticore)
* [Mythril](https://github.com/ConsenSys/mythril)
* ...

## Contact

Creator: Patrick Ventuzelo - @Pat_Ventuzelo
