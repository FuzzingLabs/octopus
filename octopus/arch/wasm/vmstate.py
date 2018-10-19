from octopus.engine.engine import VMstate


class WasmVMstate(VMstate):

    def __init__(self):

        self.memory = []

        self.stack = []
        self.ssa_stack = []
        self.symbolic_stack = []

        self.last_returned = []
        self.pc = 0
        self.instr = None

        self.instructions_visited = list()
        #self.instructions_visited = dict()

    def details(self):

        return {'memory': self.memory,
                'stack': self.stack,
                'ssa_stack': self.ssa_stack,
                'symbolic_stack': self.symbolic_stack,
                'last_returned': self.last_returned,
                'pc': self.pc}
