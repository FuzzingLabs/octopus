from octopus.arch.evm.cfg import EvmCFG


# Etherem smart contract == EVM bytecode
class EthereumCFG(EvmCFG):
    def __init__(self, bytecode, analysis='dynamic'):
        EvmCFG.__init__(self,
                        bytecode=bytecode,
                        analysis=analysis)
