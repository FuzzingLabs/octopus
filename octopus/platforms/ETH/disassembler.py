from octopus.arch.evm.disassembler import EvmDisassembler
from octopus.arch.wasm.disassembler import WasmDisassembler


# Etherem smart contract == EVM bytecode
class EthereumDisassembler(object):
    def __new__(cls, bytecode=None, arch='evm'):
        if arch == 'evm':
            return EvmDisassembler(bytecode)
        else:  # Wasm
            return WasmDisassembler(bytecode)
