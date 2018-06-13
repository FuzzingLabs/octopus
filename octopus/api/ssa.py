SSA_TYPE_FUNCTION = "function"
SSA_TYPE_CONSTANT = "constant"


class SSA(object):
    '''TODO'''

    def __init__(self, new_assignement=None, method_name=None, args=None, instr_type=SSA_TYPE_FUNCTION):
        """ TODO """
        self.new_assignement = new_assignement
        self.method_name = method_name
        self.args = args
        self.instr_type = instr_type

    def detail(self):
        out = ''
        out += 'new_assignement = ' + str(self.new_assignement) + '\n'
        out += 'method_name = ' + str(self.method_name) + '\n'
        out += 'args = ' + str(self.args) + '\n'
        out += 'instr_type = ' + str(self.instr_type) + '\n'
        out += '\n\n'
        return out

    def format(self):
        out = ''
        if self.is_constant:
            if self.new_assignement != None:
                out += '%{:02X}'.format(self.new_assignement)
                out += ' = '
            if self.args != None:
                out += '#0x%X' % self.args
            #if self.method_name:
            #    out += ' (%s)' % self.method_name
        elif self.is_function:
            if self.new_assignement != None:
                out += '%{:02X}'.format(self.new_assignement)
                out += ' = '
            if self.method_name:
                out += '%s(' % self.method_name
            if self.args != None:
                out += ', '.join('%{:02X}'.format(arg.ssa.new_assignement) for arg in self.args)
            out += ')'
        else:
            raise Exception('ssa_format no instr_type ')
        return out

    @property
    def is_constant(self):
        """ TODO """
        return self.instr_type == SSA_TYPE_CONSTANT

    @property
    def is_function(self):
        """ TODO """
        return self.instr_type == SSA_TYPE_FUNCTION
