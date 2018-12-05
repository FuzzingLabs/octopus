#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

from logging import getLogger
logging = getLogger(__name__)


PLATFORM = 'wasm'


def error_print(msg):
    print('[X] %s for %s' % (msg, PLATFORM))
    sys.exit()


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Security Analysis tool for WebAssembly module and Blockchain Smart Contracts (BTC/ETH/NEO/EOS)')

    inputs = parser.add_argument_group('Input arguments')
    inputs.add_argument('-r', '--raw',
                        help='hex-encoded bytecode string ("ABcdeF09..." or "0xABcdeF09...")',
                        metavar='BYTECODE')
    inputs.add_argument('-f', '--file',
                        type=argparse.FileType('rb'),
                        help='binary file (.wasm)',
                        metavar='WASMMODULE')

    features = parser.add_argument_group('Features')
    features.add_argument('-d', '--disassemble',
                          action='store_true',
                          help='print text disassembly ')
    features.add_argument('-z', '--analyzer',
                          action='store_true',
                          help='print module information')
    features.add_argument('-y', '--analytic',
                          action='store_true',
                          help='print Functions instructions analytics')
    features.add_argument('-g', '--cfg',
                          action='store_true',
                          help='generate the control flow graph (CFG)')
    features.add_argument('-c', '--call',
                          action='store_true',
                          help='generate the call flow graph')
    features.add_argument('-s', '--ssa',
                          action='store_true',
                          help='generate the CFG with SSA representation')

    graph = parser.add_argument_group('Graph options')
    graph.add_argument('--simplify', action='store_true',
                       help='generate a simplify CFG')
    graph.add_argument('--functions', action='store_true',
                       help='create subgraph for each function')
    graph.add_argument('--onlyfunc', type=str,
                       nargs="*",
                       default=[],
                       help='only generate the CFG for this list of function name')
    #graph.add_argument('--visualize',
    #                   help='direcly open the CFG file')
    #graph.add_argument('--format',
    #                   choices=['pdf', 'png', 'dot'],
    #                   default='pdf',
    #                   help='direcly open the CFG file')

    args = parser.parse_args()

    octo_bytecode = None
    octo_analyzer = None
    octo_disasm = None
    octo_cfg = None

    # process input code
    if args.raw:
        octo_bytecode = args.raw
    elif args.file:
        octo_bytecode = args.file.read()

    # Disassembly
    if args.disassemble:
        from octopus.arch.wasm.disassembler import WasmDisassembler

        # TODO add other r_format support
        octo_disasm = WasmDisassembler()
        print(octo_disasm.disassemble_module(octo_bytecode, r_format='text'))

    if args.analyzer:
        from octopus.arch.wasm.analyzer import WasmModuleAnalyzer

        octo_analyzer = WasmModuleAnalyzer(octo_bytecode)
        print(octo_analyzer)

    # Control Flow Analysis & Call flow Analysis
    if args.cfg or args.call or args.analytic:
        from octopus.arch.wasm.cfg import WasmCFG
        from octopus.analysis.graph import CFGGraph

        octo_cfg = WasmCFG(octo_bytecode)

        if args.call:
            octo_cfg.visualize_call_flow()
        if args.analytic:
            octo_cfg.visualize_instrs_per_funcs()

        if args.cfg:
            octo_graph = CFGGraph(octo_cfg)
            if args.functions or args.onlyfunc:
                octo_graph.view_functions(only_func_name=args.onlyfunc,
                                          simplify=args.simplify,
                                          ssa=args.ssa)
            else:
                octo_graph.view(simplify=args.simplify, ssa=args.ssa)

    if args.ssa:
        from octopus.arch.wasm.emulator import WasmSSAEmulatorEngine

        emul = WasmSSAEmulatorEngine(octo_bytecode)
        # run the emulator for SSA
        if args.onlyfunc:
            emul.emulate_functions(args.onlyfunc)
        # try to emulate main by default
        else:
            emul.emulate_functions()

        # visualization of the cfg with SSA
        emul.cfg.visualize(ssa=True)

    if not args.disassemble and not args.ssa \
            and not args.cfg and not args.call\
            and not args.analyzer and not args.analytic:
        parser.print_help()


if __name__ == '__main__':
    main()
