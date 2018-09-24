from octopus.arch.evm.cfg import EvmCFG
from octopus.arch.wasm.cfg import WasmCFG


# Ethereum smart contract == EVM bytecode or WebAssembly
class EthereumCFG(object):
    def __new__(cls, bytecode, arch='evm', evm_analysis='dynamic'):
        if arch == 'evm':
            return EvmCFG(bytecode, analysis=evm_analysis)
        else:  # Wasm
            return WasmCFG(bytecode)
