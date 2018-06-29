class Contract(object):

    def __init__(self, name="default_contract_name",
                 address=None, balance=None, bytecode=None,
                 abi=None, source_code=None):
        self.name = name
        self.address = address
        self.balance = balance
        self.bytecode = bytecode
        self.abi = abi
        self.source_code = source_code
        self.info = {}

    def get_online_bytecode(self, explorer):
        raise NotImplementedError

    def get_online_abi(self, explorer):
        raise NotImplementedError

    def get_online_source(self, explorer):
        raise NotImplementedError

    def get_online_info(self, explorer):
        raise NotImplementedError
