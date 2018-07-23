from octopus.arch.evm.disassembler import EvmDisassembler


# Etherem smart contract == EVM bytecode
class EthereumDisassembler(EvmDisassembler):
    def __init__(self, bytecode=None):
        EvmDisassembler.__init__(self,
                                 bytecode=bytecode)
