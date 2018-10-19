from octopus.engine.engine import VMstate


class EvmVMstate(VMstate):

    def __init__(self, gas=1000000):
        self.storage = {}
        self.memory = []

        self.stack = []
        self.ssa_stack = []
        self.symbolic_stack = []

        self.last_returned = []
        self.gas = gas
        self.pc = 0
        self.instr = None

        self.instructions_visited = list()

    def details(self):

        return {'storage': self.storage,
                'memory': self.memory,
                'stack': self.stack,
                'ssa_stack': self.ssa_stack,
                'symbolic_stack': self.symbolic_stack,
                'last_returned': self.last_returned,
                'gas': self.gas,
                'pc': self.pc}
