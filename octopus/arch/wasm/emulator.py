from octopus.engine.emulator import EmulatorEngine
from octopus.arch.wasm.cfg import WasmCFG
from octopus.arch.wasm.vmstate import WasmVMstate
from octopus.core.ssa import SSA, SSA_TYPE_FUNCTION, SSA_TYPE_CONSTANT

from octopus.arch.wasm.format import (format_func_name,
                                      format_bb_name)

import copy

from logging import getLogger
logging = getLogger(__name__)

# =======================================
# #         WASM Emulator               #
# =======================================


class WasmEmulatorEngine(EmulatorEngine):

    def __init__(self, bytecode):
        raise NotImplementedError


class WasmSSAEmulatorEngine(EmulatorEngine):

    def __init__(self, bytecode):

        # retrive instructions, basicblocks & functions statically
        self.cfg = WasmCFG(bytecode)
        self.ana = self.cfg.analyzer

        self.current_function = None
        self.current_f_instructions = None
        self.reverse_instructions = dict()
        self.current_f_basicblocks = None

        self.basicblock_per_instr = dict()
        self.current_basicblock = None

        # connection between basicblocks
        # will be generate dynamically by the Emulator

        self.states = dict()
        self.states_total = 0
        self.ssa_counter = 0

        logging.warning("Function available: %s" % [x.name for x in self.cfg.functions])

    def emulate_functions(self, list_functions_name=None, state=WasmVMstate(), depth=0):

        if list_functions_name:
            if set(list_functions_name).issubset([x.name for x in self.cfg.functions]):  # function_name not in [x.name for x in self.functions]:
                raise Exception('Some function_name given not in this module - available: %s', self.ana.func_prototypes)
        else:
            list_functions_name = [x.name for x in self.cfg.functions]
        for f in list_functions_name:
            self.emulate_one_function(function_name=f, state=state, depth=depth)

    def emulate_one_function(self, function_name, state=WasmVMstate(), depth=0):

        if function_name not in [x.name for x in self.cfg.functions]:
            raise Exception('function_name not in this module - available: %s', self.ana.func_prototypes)

        self.current_function = self.cfg.get_function(function_name)
        self.current_f_instructions = self.current_function.instructions
        self.reverse_instructions = {k: v for k, v in enumerate(self.current_f_instructions)}
        self.current_f_basicblocks = self.current_function.basicblocks

        # create dict with:
        # * key = instruction offset
        # * value = basicblock reference
        # easy to get the corresponding basicblock per instr now
        for bb in self.current_f_basicblocks:
            for intr in bb.instructions:
                self.basicblock_per_instr[intr.offset] = bb

        # connection between basicblocks
        # will be generate dynamically by the Emulator

        self.states = dict()
        self.states_total = 0
        self.ssa_counter = 0

        logging.warning("[+] current_function detected - %x: %s/%s",
                        self.current_function.start_offset,
                        self.current_function.name,
                        self.current_function.prefered_name)

        # launch emulation
        self.emulate(state=state, depth=depth)

    def emulate(self, state=WasmVMstate(), depth=0):

        #  create fake stack for tests
        state.symbolic_stack = list(range(1000))

        # get current instruction
        instr = self.reverse_instructions[state.pc]

        # create the first basicblock of this branch
        # print('%d : %s' % (instr.offset, instr.name))
        self.current_basicblock = self.basicblock_per_instr[instr.offset]

        # beginning of a function
        #if instr in self.functions_start_instr:
            # retrive matching function
        #    self.current_function = next(filter(lambda f: f.start_instr == instr, self.functions))
            # self.ssa_counter = 0
        logging.warning("[+] Entering function - %x: %s",
                        self.current_function.start_offset,
                        self.current_function.prefered_name)

        # associate function to basicblock
        # TODO: create list of function_name
        self.current_basicblock.function_name = self.current_function.prefered_name
        # associate basicblock to function
        self.current_function.basicblocks.append(self.current_basicblock)

        # halt variable use to catch ending branch
        halt = False
        while not halt:

            # get current instruction
            instr = self.reverse_instructions[state.pc]

            # get current basicblock
            self.current_basicblock = self.basicblock_per_instr[instr.offset]

            # add this instruction to his functions
            # TODO: verify if it's not useless for ethereum
            #self.current_function.instructions.append(instr)

            # Save instruction and state
            state.instr = instr
            self.states[self.states_total] = state
            state = copy.deepcopy(state)
            self.states_total += 1
            state.pc += 1

            # execute single instruction
            halt = self.emulate_one_instruction(instr, state, depth)
            state.instructions_visited.append(instr.offset)
            #state.instructions_visited[instr.offset] = instr.offset

        logging.warning("[X] Returning from basicblock %s", self.current_basicblock.name)

        # automatic remove duplicated edges
        #self.edges = list(set(self.edges))
    '''
    is_control
    is_parametric
    is_variable
    is_memory
    is_constant
    is_logical_i32
    is_logical_i64
    is_logical_f32
    is_logical_f64
    is_arithmetic_i32
    is_bitwise_i32
    is_arithmetic_i64
    is_bitwise_i64
    is_arithmetic_f32
    is_arithmetic_f64
    is_conversion
    '''

    def emulate_one_instruction(self, instr, state, depth):

        halt = False

        logging.warning('--')
        logging.warning('stack %s' % state.ssa_stack)
        logging.warning('instr %s' % instr.name)
        logging.warning('operand %s' % instr.operand)
        logging.warning('xref %s' % instr.xref)

        if instr.is_control:
            halt = self.emul_control_instr(instr, state, depth)

        elif instr.is_parametric:
            halt = self.emul_parametric_instr(instr, state)

        elif instr.is_variable:
            halt = self.emul_variable_instr(instr, state)

        elif instr.is_memory:
            halt = self.emul_memory_instr(instr, state)

        elif instr.is_constant:
            halt = self.emul_constant_instr(instr, state)

        elif instr.is_logical_i32:
            halt = self.emul_logical_i32_instr(instr, state)

        elif instr.is_logical_i64:
            halt = self.emul_logical_i64_instr(instr, state)

        elif instr.is_logical_f32:
            halt = self.emul_logical_f32_instr(instr, state)

        elif instr.is_logical_f64:
            halt = self.emul_logical_f64_instr(instr, state)

        elif instr.is_arithmetic_i32:
            halt = self.emul_arithmetic_i32_instr(instr, state)

        elif instr.is_bitwise_i32:
            halt = self.emul_bitwise_i32_instr(instr, state)

        elif instr.is_arithmetic_i64:
            halt = self.emul_arithmetic_i64_instr(instr, state)

        elif instr.is_bitwise_i64:
            halt = self.emul_bitwise_i64_instr(instr, state)

        elif instr.is_arithmetic_f32:
            halt = self.emul_arithmetic_f32_instr(instr, state)

        elif instr.is_arithmetic_f64:
            halt = self.emul_arithmetic_f64_instr(instr, state)

        elif instr.is_conversion:
            halt = self.emul_conversion_instr(instr, state)

        # UNKNOWN INSTRUCTION
        else:
            logging.warning('UNKNOWN = ' + instr.name)

        return halt

    def emul_control_instr(self, instr, state, depth):
        halt = False
        if instr.name == 'unreachable':
            instr.ssa = SSA(method_name=instr.name)
            halt = True
        elif instr.name in ['nop', 'block', 'loop', 'else']:
            instr.ssa = SSA(method_name=instr.name)
        elif instr.name == 'if':
            arg = [state.ssa_stack.pop()]
            instr.ssa = SSA(method_name=instr.name, args=arg)
            # TODO branch if
            # inst + 1 == true block
            # need to find offset false block using edges or basicblocks list
            logging.warning('SSA: branch if not yet supported')
        elif instr.name == 'end':
            instr.ssa = SSA(method_name=instr.name)
            # check if it's the last instructions of the function
            if instr.offset == self.current_f_instructions[-1].offset:
                logging.warning("[X] break %s" % instr.name)
                halt = True
        elif instr.name == 'br':
            instr.ssa = SSA(method_name=instr.name)
            jump_addr = instr.xref

            # get instruction with this value as offset
            target = next(filter(lambda element: element.offset == jump_addr[0], self.current_f_instructions))

            if target.offset not in state.instructions_visited:
                # condition are True
                logging.warning('[X] follow br branch offset 0x%x' % (target.offset))
                new_state = copy.deepcopy(state)
                new_state.pc = self.current_f_instructions.index(target)
                # follow the br
                self.emulate(new_state, depth=depth + 1)
            else:
                logging.warning('[X] Loop detected, skipping br 0x%x' % jump_addr[0])
                halt = True
            halt = True

        elif instr.name == 'br_if':
            arg = [state.ssa_stack.pop()]
            instr.ssa = SSA(method_name=instr.name, args=arg)

            logging.warning('[X] follow br_if default branch offset 0x%x' % (instr.offset_end + 1))
            new_state = copy.deepcopy(state)

            self.emulate(new_state, depth=depth + 1)
            # after we return from emul - restore current_basicblock
            self.current_basicblock = self.basicblock_per_instr[instr.offset]

            jump_addr = instr.xref
            # get instruction with this value as offset
            target = next(filter(lambda element: element.offset == jump_addr[0], self.current_f_instructions))

            if target.offset not in state.instructions_visited:
                # condition are True
                logging.warning('[X] follow br_if branch offset 0x%x' % (target.offset))
                new_state = copy.deepcopy(state)
                new_state.pc = self.current_f_instructions.index(target)

                # follow the br_if
                self.emulate(new_state, depth=depth + 1)

            else:
                logging.warning('[X] Loop detected, skipping br_if 0x%x' % jump_addr[0])
                halt = True
            halt = True
        elif instr.name == 'br_table':
            arg = [state.ssa_stack.pop()]
            instr.ssa = SSA(method_name=instr.name, args=arg)
            # TODO branch br_table
            logging.warning('SSA: branch br_table not yet supported')
        elif instr.name == 'return':
            arg = [state.ssa_stack.pop()]
            instr.ssa = SSA(method_name=instr.name, args=arg)
            halt = True
        elif instr.name == 'call':
            f_offset = int.from_bytes(instr.operand, 'big')
            target_func = self.ana.func_prototypes[f_offset]
            name, param_str, return_str, f_type = target_func
            # format_func_name()
            instr.ssa = SSA(method_name=instr.name + '_to_' + name)
            if param_str:
                num_arg = len(param_str.split(' '))
                #print(hex(state.ssa_stack[-1].offset))
                arg = [state.ssa_stack.pop() for x in range(1, num_arg+1)]
                instr.ssa.args = arg
            if return_str:
                instr.ssa.new_assignement = self.ssa_counter
                state.ssa_stack.append(instr)
                self.ssa_counter += 1
        elif instr.name == 'call_indirect':
            arg = [state.ssa_stack.pop()]
            ''' # issue when table is imported
            # arg is constant
            if arg[0].ssa.instr_type == SSA_TYPE_CONSTANT:
                f_offset = int.from_bytes(instr.operand, 'big')
                target_func = self.ana.func_prototypes[f_offset]

                name, param_str, return_str, f_type = target_func
                # format_func_name()
                instr.ssa = SSA(method_name=instr.name + '_to_' + name)
                if param_str:
                    num_arg = len(param_str.split(' '))
                    print(hex(state.ssa_stack[-1].offset))
                    arg = [state.ssa_stack.pop() for x in range(1, num_arg+1)]
                    instr.ssa.args = arg
                if return_str:
                    instr.ssa.new_assignement = self.ssa_counter
                    state.ssa_stack.append(instr)
                    self.ssa_counter += 1
            else:
            '''
            instr.ssa = SSA(method_name=instr.name, args=arg)
            # test if arg is constant --> do like call
            # else - stay like that
        return halt

    def emul_parametric_instr(self, instr, state):
        if instr.name == 'drop':
            state.ssa_stack.pop()
            instr.ssa = SSA(method_name=instr.name)
        else:  # select
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop()]
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1
        return False

    def emul_variable_instr(self, instr, state):
        if instr.name in ['get_local', 'get_global']:
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1
        elif instr.name in ['set_local', 'set_global']:
            state.ssa_stack.pop()
            instr.ssa = SSA(method_name=instr.name)
        elif instr.name == 'tee_local':
            state.ssa_stack.append(state.ssa_stack[-1])
            self.ssa_counter += 1
        return False

    def emul_memory_instr(self, instr, state):
        # load
        if 'load' in instr.name:
            arg = [state.ssa_stack.pop()]
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif 'store' in instr.name:
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
            instr.ssa = SSA(method_name=instr.name, args=arg)

        elif instr.name == 'current_memory':
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1
        else:
            instr.ssa = SSA(method_name=instr.name)
        return False

    def emul_constant_instr(self, instr, state):
        op = int.from_bytes(instr.operand, byteorder='big')
        instr.ssa = SSA(self.ssa_counter, instr.name,
                        op,
                        instr_type=SSA_TYPE_CONSTANT)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1
        return False

    def emul_logical_i32_instr(self, instr, state):
        if instr.name == 'i32.eqz':
            arg = [state.ssa_stack.pop()]
        else:
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_logical_i64_instr(self, instr, state):
        if instr.name == 'i64.eqz':
            arg = [state.ssa_stack.pop()]
        else:
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_logical_f32_instr(self, instr, state):
        arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_logical_f64_instr(self, instr, state):
        arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_arithmetic_i32_instr(self, instr, state):
        if instr.name in ['i32.clz', 'i32.ctz', 'i32.popcnt']:
            arg = [state.ssa_stack.pop()]
        else:
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_bitwise_i32_instr(self, instr, state):
        arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_arithmetic_i64_instr(self, instr, state):
        if instr.name in ['i64.clz', 'i64.ctz', 'i64.popcnt']:
            arg = [state.ssa_stack.pop()]
        else:
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_bitwise_i64_instr(self, instr, state):
        arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_arithmetic_f32_instr(self, instr, state):
        if instr.name in ['f32.abs', 'f32.neg']:
            arg = [state.ssa_stack.pop()]
        else:
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_arithmetic_f64_instr(self, instr, state):
        if instr.name in ['f64.abs', 'f64.neg']:
            arg = [state.ssa_stack.pop()]
        else:
            arg = [state.ssa_stack.pop(), state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False

    def emul_conversion_instr(self, instr, state):
        arg = [state.ssa_stack.pop()]
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=arg)
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

        return False
