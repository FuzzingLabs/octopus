class Contract(object):

    def __init__(self, name="default_contract_name", address=None, balance=None, bytecode=None, abi=None, cfg=None):
        self.name = name
        self.address = address
        self.balance = balance
        self.bytecode = bytecode
        self.abi = abi
