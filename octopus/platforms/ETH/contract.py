from octopus.core.contract import Contract


class ContractAdressEmptyException(Exception):
    """Exception raised when address is None"""
    pass


class EthereumContract(Contract):

    @property
    def _address_defined(self):
        if self.address is None:
            raise ContractAdressEmptyException()
        return True

    def get_online_bytecode(self, explorer):
        if self._address_defined:
            self.bytecode = explorer.eth_getCode(self.address)

    def get_online_abi(self, explorer):
        raise NotImplementedError

    def get_online_source(self, explorer):
        raise NotImplementedError

    def get_online_info(self, explorer):
        # get the balance
        if self._address_defined:
            # self.name
            self.balance = explorer.eth_getBalance(self.address)
            self.bytecode = explorer.eth_getCode(self.address)
            # self.abi
            # self.source_code
