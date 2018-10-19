from octopus.arch.evm.emulator import EvmEmulatorEngine
from octopus.arch.wasm.emulator import WasmEmulatorEngine
from octopus.arch.evm.emulator import EvmSSAEngine
from octopus.arch.wasm.emulator import WasmSSAEmulatorEngine


class EthereumEmulatorEngine(object):
    def __new__(cls, bytecode, arch='evm'):
        if arch == 'evm':
            return EvmEmulatorEngine(bytecode)
        else:  # Wasm
            return WasmEmulatorEngine(bytecode)


class EthereumSSAEngine(object):
    def __new__(cls, bytecode, arch='evm', max_depth=20):
        if arch == 'evm':
            return EvmSSAEngine(bytecode, max_depth=max_depth)
        else:  # Wasm
            return WasmSSAEmulatorEngine(bytecode)
