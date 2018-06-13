BASICBLOCK_TERMINAL = 'terminal'
BASICBLOCK_UNCONDITIONAL = 'unconditional'
BASICBLOCK_CONDITIONAL = 'conditional'
BASICBLOCK_FALLTHROUGH = 'fallthrough'
BASICBLOCK_DEFAULT = 'default'


class BasicBlock(object):
    """
    TODO: remove bb type and replace it in the code direcly with edges
    """
    def __init__(self, start_offset=0x00, start_instr=None,
                 bb_type=BASICBLOCK_DEFAULT, name='block_default_name'):
        self.start_offset = start_offset
        self.start_instr = start_instr
        self.type = bb_type  # default
        self.name = name
        self.end_offset = start_offset
        self.end_instr = start_instr
        self.instructions = list()

        self.states = []
        self.function_name = "unknown"

    @property
    def size(self):
        return self.end_offset - self.start_offset

    @property
    def is_terminal(self):
        return self.type == BASICBLOCK_TERMINAL

    @property
    def is_unconditional(self):
        return self.type == BASICBLOCK_UNCONDITIONAL

    @property
    def is_conditional(self):
        return self.type == BASICBLOCK_CONDITIONAL

    @property
    def is_fallthrough(self):
        return self.type == BASICBLOCK_FALLTHROUGH

    @property
    def is_default(self):
        return self.type == BASICBLOCK_DEFAULT

    def show(self):
        out = ''
        line = ''
        line = str(self.start_offset) + ': ' + str(self.name) + '\n'
        line += 'start_instr = ' + str(self.start_instr.name) + '\n'
        line += 'size = ' + str(self.size) + '\n'
        line += 'type = ' + str(self.type) + '\n'
        line += 'end_offset = ' + str(self.end_offset) + '\n'
        line += 'end_instr = ' + str(self.end_instr.name) + '\n'
        line += 'function_name = ' + str(self.function_name) + '\n'
        out += line + '\n\n'
        return out

    def instructions_details(self, format='hex'):
        out = ''
        line = ''
        for i in self.instructions:
            line = '%x: ' % i.offset
            #line += '' + i.name

            if i.operand is not None and not i.xref:
                line += '%s' % str(i)#int.from_bytes(i.operand, byteorder='big')
            elif i.xref:
                line += '%s %x' % (i.name, i.xref)
            else:
                line += i.name + ' '

            out += line + '\n'
        return out

    def instructions_ssa(self, format='hex'):
        out = ''
        line = ''
        for i in self.instructions:
            line = '%x: ' % i.offset
            if i.ssa:
                line += '' + i.ssa.format()
            else:
                line += '[NO_SSA] ' + i.name
            out += line + '\n'
        return out
