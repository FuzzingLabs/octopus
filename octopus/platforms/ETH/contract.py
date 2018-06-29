from octopus.api.contract import Contract


class EthereumContract(Contract):

    def get_online_bytecode(self, explorer):
        if self.address:
            self.bytecode = explorer.eth_getCode(self.address)
        else:
            raise ValueError('self.address is None')

    def get_online_abi(self, explorer):
        raise NotImplementedError

    def get_online_source(self, explorer):
        raise NotImplementedError

    def get_online_info(self, explorer):
        raise NotImplementedError
