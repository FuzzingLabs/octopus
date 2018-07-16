from octopus.api.edge import Edge, EDGE_UNCONDITIONAL, EDGE_CONDITIONAL_TRUE, EDGE_CONDITIONAL_FALSE, EDGE_FALLTHROUGH, EDGE_CALL
from octopus.api.engine import SSAEngine
from octopus.api.optimizer import SSAOptimizer
from octopus.api.ssa import SSA, SSA_TYPE_FUNCTION, SSA_TYPE_CONSTANT

from octopus.platforms.ETH.vmstate import EthereumVMstate
from octopus.platforms.ETH.cfg import EthereumCFG

from octopus.platforms.ETH.disassembler import EthereumDisassembler
from octopus.platforms.ETH.emulator import EthereumEmulatorEngine

import copy
import logging
logging.basicConfig(level=logging.WARN)


class EthereumSSAEngine(EthereumEmulatorEngine):

    def __init__(self, bytecode=None, max_depth=20):
        EthereumEmulatorEngine.__init__(self, bytecode=bytecode, ssa=True, symbolic_exec=False, max_depth=20)
        if not bytecode and not instructions:
            raise Exception("No bytecode/instructions provided")
        if instructions:
            self.instructions = instructions
        else:
            # disassemble bytecode to instructions
            disasm = EthereumDisassembler(bytecode)
            self.instructions = disasm.disassemble()
        self.ssaoptimizer = SSAOptimizer()

        self.reverse_instructions = {k: v for k, v in enumerate(self.instructions)}

        # retrive basicblocks & functions statically
        self.cfg = EthereumCFG(instructions=self.instructions, analysis='static')
        self.functions = self.cfg.functions
        self.basicblocks = self.cfg.basicblocks

        self.functions_start_instr = [f.start_instr for f in self.functions]
        self.current_function = self.functions[0]
        self.basicblock_per_instr = dict()
        self.current_basicblock = None

        # create dict with:
        # * key = instruction offset
        # * value = basicblock reference
        # easy to get the corresponding basicblock per instr now
        for bb in self.basicblocks:
            for intr in bb.instructions:
                self.basicblock_per_instr[intr.offset] = bb

        # connection between basicblocks
        self.edges = list()

        self.states = dict()
        self.states_total = 0
        self.max_depth = max_depth
        self.ssa_counter = 0

        logging.info("=======================================")
        logging.info("#         Ethereum SSA Engine         #")
        logging.info("=======================================")
        logging.info("[+] Functions detected : %s", [f.prefered_name for f in self.functions])

    def emulate(self, state=EthereumVMstate(), depth=0):

        #  create fake stack for test
        state.symbolic_stack = list(range(1000))

        # get current instruction
        instr = self.reverse_instructions[state.pc]

        # create the first basicblock of this branch
        # print('%d : %s' % (instr.offset, instr.name))
        self.current_basicblock = self.basicblock_per_instr[instr.offset]

        # beginning of a function
        if instr in self.functions_start_instr:
            # retrive matching function
            self.current_function = next(filter(lambda f: f.start_instr == instr, self.functions))
            self.ssa_counter = 0
            logging.info("[+] Entering function:" + self.current_function.prefered_name + ' at ' + str(hex(self.current_function.start_offset)))

        # associate function to basicblock
        self.current_basicblock.function_name = self.current_function.prefered_name
        # associate basicblock to function
        self.current_function.basicblocks.append(self.current_basicblock)

        # halt variable use to catch end branch
        halt = False
        while not halt:

            # get current instruction
            instr = self.reverse_instructions[state.pc]

            # handle fall-thrown due to JUMPDEST
            if instr.name == 'JUMPDEST':
                # doesn't match new block that start with JUMPDEST
                if self.current_basicblock.start_offset != instr.offset:
                    self.edges.append(Edge(self.current_basicblock.name, 'block_%x'%instr.offset, EDGE_FALLTHROUGH))

            # get current basicblock
            self.current_basicblock = self.basicblock_per_instr[instr.offset]

            # add this instruction to his functions
            self.current_function.instructions.append(instr)

            # Save instruction and state
            state.instr = instr
            self.states[self.states_total] = state
            state = copy.deepcopy(state)
            self.states_total += 1
            state.pc += 1

            # execute single instruction
            halt = self.emulate_one_instruction(instr, state, depth)
            state.instructions_visited.append(instr.offset)

        logging.info("[X] Returning from basicblock %s" % self.current_basicblock.name)

        # automatic remove doublon edges
        self.edges = list(set(self.edges))

    def emulate_one_instruction(self, instr, state, depth):

        halt = False

        #
        #  0s: Stop and Arithmetic Operations
        #
        if instr.name == 'STOP':
            instr.ssa = SSA(method_name=instr.name)
            halt = True
        elif instr.is_arithmetic:
            self.ssa_arithmetic_instruction(instr, state)
        #
        #  10s: Comparison & Bitwise Logic Operations
        #
        elif instr.is_comparaison_logic:
            self.ssa_comparaison_logic_instruction(instr, state)
        #
        #  20s: SHA3
        #
        elif instr.is_sha3:
            self.ssa_sha3_instruction(instr, state)
        #
        #  30s: Environment Information
        #
        elif instr.is_environmental:
            self.ssa_environmental_instruction(instr, state)
        #
        #  40s: Block Information
        #
        elif instr.uses_block_info:
            self.ssa_block_instruction(instr, state)
        #
        #  50s: Stack, Memory, Storage, and Flow Information
        #
        elif instr.uses_stack_block_storage_info:
            halt = self.ssa_stack_memory_storage_flow_instruction(instr, state, depth)
        #
        #  60s & 70s: Push Operations
        #
        elif instr.name.startswith("PUSH"):
            #value = int.from_bytes(instr.operand, byteorder='big')
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name,
                            args=instr.operand_interpretation,
                            instr_type=SSA_TYPE_CONSTANT)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1
        #
        #  80s: Duplication Operations
        #
        elif instr.name.startswith('DUP'):
            # DUPn (eg. DUP1: a b c -> a b c c, DUP3: a b c -> a b c a)
            position = instr.pops  # == XX from DUPXX
            try:
                # SSA STACK
                instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[state.ssa_stack[- position]])
                state.ssa_stack.append(state.ssa_stack[- position])
                self.ssa_counter += 1
                halt = False
            except:
                logging.info('[-] STACK underflow')
                halt = True
        #
        #  90s: Swap Operations
        #
        elif instr.name.startswith('SWAP'):
            # SWAPn (eg. SWAP1: a b c d -> a b d c, SWAP3: a b c d -> d b c a)
            position = instr.pops - 1  # == XX from SWAPXX
            try:
                temp = state.ssa_stack[-position - 1]
                state.ssa_stack[-position - 1] = state.ssa_stack[-1]
                state.ssa_stack[-1] = temp

                instr.ssa = SSA(method_name=instr.name, args=[temp])

                halt = False
            except:
                logging.warning('[-] STACK underflow')
                halt = True
                #raise ValueError('STACK underflow')
        #
        #  a0s: Logging Operations
        #
        elif instr.name.startswith('LOG'):
            # only stack operations emulated
            arg = [state.ssa_stack.pop() for x in range(instr.pops)]
            instr.ssa = SSA(method_name=instr.name, args=arg)
            #state.ssa_stack.append(instr)
        #
        #  f0s: System Operations
        #
        elif instr.is_system:
            halt = self.ssa_system_instruction(instr, state)
            #ssa.append(instr.name)

        # UNKNOWN INSTRUCTION
        else:
            logging.warning('UNKNOWN = ' + instr.name)

        return halt

    def ssa_arithmetic_instruction(self, instr, state):

        if instr.name in ['ADD', 'SUB', 'MUL', 'DIV', 'MOD', 'SDIV', 'SMOD', 'EXP', 'SIGNEXTEND']:
            # SSA STACK
            s0, s1 = state.ssa_stack.pop(), state.ssa_stack.pop()
            instr.ssa = SSA(new_assignement=self.ssa_counter,
                            method_name=instr.name, args=[s0, s1])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif instr.name in ['ADDMOD', 'MULMOD']:
            # SSA STACK
            s0, s1, s2 = state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop()
            instr.ssa = SSA(new_assignement=self.ssa_counter,
                            method_name=instr.name, args=[s0, s1, s2])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

    def ssa_comparaison_logic_instruction(self, instr, state):

        if instr.name in ['LT', 'GT', 'SLT', 'SGT', 'EQ', 'AND', 'OR', 'XOR', 'BYTE']:
            # SSA STACK
            s0, s1 = state.ssa_stack.pop(), state.ssa_stack.pop()
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[s0, s1])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif instr.name in ['ISZERO', 'NOT']:
            # SSA STACK
            s0 = state.ssa_stack.pop()
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[s0])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

    def ssa_sha3_instruction(self, instr, state):
        '''Symbolic execution of SHA3 group of opcode'''

        # SSA STACK
        s0, s1 = state.ssa_stack.pop(), state.ssa_stack.pop()
        instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[s0, s1])
        state.ssa_stack.append(instr)
        self.ssa_counter += 1

    def ssa_environmental_instruction(self, instr, state):

        if instr.name in ['ADDRESS', 'ORIGIN', 'CALLER', 'CALLVALUE', 'CALLDATASIZE', 'CODESIZE', 'RETURNDATASIZE', 'GASPRICE']:
            # SSA STACK
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif instr.name in ['BALANCE', 'CALLDATALOAD', 'EXTCODESIZE']:
            # SSA STACK
            s0 = state.ssa_stack.pop()
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[s0])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif instr.name in ['CALLDATACOPY', 'CODECOPY', 'RETURNDATACOPY']:
            op0, op1, op2 = state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop()
            # SSA STACK
            instr.ssa = SSA(method_name=instr.name, args=[op0, op1, op2])

        elif instr.name == 'EXTCODECOPY':
            addr = state.ssa_stack.pop()
            start, s2, size = state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop()
            # SSA STACK
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[addr, start, s2, size])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

    def ssa_block_instruction(self, instr, state):

        if instr.name == 'BLOCKHASH':
            # SSA STACK
            blocknumber = state.ssa_stack.pop()
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[blocknumber])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif instr.name in ['COINBASE', 'TIMESTAMP', 'NUMBER', 'DIFFICULTY', 'GASLIMIT']:
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

    def ssa_stack_memory_storage_flow_instruction(self, instr, state, depth):

        halt = False
        op = instr.name

        if op == 'POP':
            # SSA STACK
            s0 = state.ssa_stack.pop()
            instr.ssa = SSA(method_name=instr.name)

        elif op in ['MLOAD', 'SLOAD']:
            # SSA STACK
            s0 = state.ssa_stack.pop()
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=[s0])
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif op in ['MSTORE', 'MSTORE8', 'SSTORE']:
            # SSA STACK
            s0, s1 = state.ssa_stack.pop(), state.ssa_stack.pop()
            instr.ssa = SSA(method_name=instr.name, args=[s0, s1])

        elif op == 'JUMP':
            # SSA STACK
            push_instr = state.ssa_stack.pop()
            instr.ssa = SSA(method_name=instr.name, args=[push_instr])

            # get instruction with this value as offset
            if push_instr.ssa.is_constant:
                #jump_addr = int.from_bytes(push_instr.operand, byteorder='big')
                jump_addr = push_instr.operand_interpretation
                # get instruction with this value as offset
                target = next(filter(lambda element: element.offset == jump_addr, self.instructions))
            else:
                # try to resolve the SSA repr
                jump_addr = self.ssaoptimizer.resolve_instr_ssa(push_instr)
                target = next(filter(lambda element: element.offset == jump_addr, self.instructions))
                if not jump_addr:
                    logging.warning('JUMP DYNAMIC TODO')
                    logging.warning('[X] push_instr %x: %s ' % (push_instr.offset, push_instr.name))
                    logging.warning('[X] push_instr.ssa %s' % push_instr.ssa.format())
                    list_args = [arg.ssa.format() for arg in push_instr.ssa.args]
                    logging.warning('[X] push_instr.ssa %s' % list_args)
                    return True

            # depth of 1 - prevent looping
            #if (depth < self.max_depth):
            if target.name != "JUMPDEST":
                logging.info('[X] Bad JUMP to 0x%x' % jump_addr)
                return True

            if target.offset not in state.instructions_visited:
                logging.info('[X] follow JUMP branch offset 0x%x' % target.offset)
                new_state = copy.deepcopy(state)
                new_state.pc = self.instructions.index(target)

                # follow the JUMP
                self.edges.append(Edge(self.current_basicblock.name, 'block_%x'%target.offset, EDGE_UNCONDITIONAL))
                self.emulate(new_state, depth=depth + 1)

                halt = True

            else:
                #logging.info('[X] Max depth reached, skipping JUMP 0x%x' % jump_addr)
                self.edges.append(Edge(self.current_basicblock.name, 'block_%x'%target.offset, EDGE_UNCONDITIONAL))
                logging.info('[X] Loop detected, skipping JUMP 0x%x' % jump_addr)
                halt = True

            self.current_basicblock = self.basicblock_per_instr[instr.offset]

        elif op == 'JUMPI':
            # SSA STACK
            push_instr, condition = state.ssa_stack.pop(), state.ssa_stack.pop()
            instr.ssa = SSA(method_name=instr.name, args=[push_instr, condition])

            logging.info('[X] follow JUMPI default branch offset 0x%x' % (instr.offset_end + 1))
            new_state = copy.deepcopy(state)
            self.edges.append(Edge(self.current_basicblock.name, 'block_%x'%(instr.offset_end + 1), EDGE_CONDITIONAL_FALSE))
            self.emulate(new_state, depth=depth + 1)
            self.current_basicblock = self.basicblock_per_instr[instr.offset]

            # get instruction with this value as offset
            if push_instr.ssa.is_constant:
                #jump_addr = int.from_bytes(push_instr.operand, byteorder='big')
                jump_addr = push_instr.operand_interpretation
                # get instruction with this value as offset
                target = next(filter(lambda element: element.offset == jump_addr, self.instructions))
            else:
                # try to resolve the SSA repr
                jump_addr = self.ssaoptimizer.resolve_instr_ssa(push_instr)
                target = next(filter(lambda element: element.offset == jump_addr, self.instructions))
                if not jump_addr:
                    logging.warning('JUMP DYNAMIC TODO')
                    logging.warning('[X] push_instr %x: %s ' % (push_instr.offset, push_instr.name))
                    logging.warning('[X] push_instr.ssa %s' % push_instr.ssa.format())
                    list_args = [arg.ssa.format() for arg in push_instr.ssa.args]
                    logging.warning('[X] push_instr.ssa %s' % list_args)
                    return True

            if target.name != "JUMPDEST":
                logging.info('[X] Bad JUMP to 0x%x' % jump_addr)
                return True

            if target.offset not in state.instructions_visited:
                # condition are True
                logging.info('[X] follow JUMPI branch offset 0x%x' % (target.offset))
                new_state = copy.deepcopy(state)
                new_state.pc = self.instructions.index(target)

                # follow the JUMPI
                self.edges.append(Edge(self.current_basicblock.name, 'block_%x'%target.offset, EDGE_CONDITIONAL_TRUE))
                self.emulate(new_state, depth=depth + 1)

            else:
                self.edges.append(Edge(self.current_basicblock.name, 'block_%x'%target.offset, EDGE_CONDITIONAL_TRUE))
                logging.warning('[X] Loop detected, skipping JUMP 0x%x' % jump_addr)
                logging.warning('[X] push_instr.ssa %s' % push_instr.ssa.format())
                halt = True
            halt = True

        elif op in ['PC', 'MSIZE', 'GAS']:
            # SSA STACK
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif op == 'JUMPDEST':
            # SSA STACK
            instr.ssa = SSA(method_name=instr.name)

        return halt

    def ssa_system_instruction(self, instr, state):

        halt = False

        if instr.name == 'CREATE':
            args = [state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop()]
            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=args)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif instr.name in ('CALL', 'CALLCODE', 'DELEGATECALL', 'STATICCALL'):

            if instr.name in ('CALL', 'CALLCODE'):
                gas, to, value, meminstart, meminsz, memoutstart, memoutsz = \
                    state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop()
                args = [gas, to, value, meminstart, meminsz, memoutstart, memoutsz]

            else:
                gas, to, meminstart, meminsz, memoutstart, memoutsz = \
                    state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop(), state.ssa_stack.pop()
                args = [gas, to, meminstart, meminsz, memoutstart, memoutsz]

            instr.ssa = SSA(new_assignement=self.ssa_counter, method_name=instr.name, args=args)
            state.ssa_stack.append(instr)
            self.ssa_counter += 1

        elif instr.name in ['RETURN', 'REVERT']:
            offset, length = state.ssa_stack.pop(), state.ssa_stack.pop()
            instr.ssa = SSA(method_name=instr.name, args=[offset, length])
            halt = True

        elif instr.name in ['INVALID', 'SELFDESTRUCT']:
            # SSA STACK
            instr.ssa = SSA(method_name=instr.name)
            halt = True

        return halt
