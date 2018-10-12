#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

from logging import getLogger
logging = getLogger(__name__)


PLATFORM = 'eth-evm'


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
                        type=argparse.FileType('r'),
                        help='file containing hex-encoded bytecode string',
                        metavar='BYTECODEFILE')
    inputs.add_argument('-a', '--address',
                        help='pull contract from the blockchain',
                        metavar='CONTRACT_ADDRESS')

    features = parser.add_argument_group('Features')
    features.add_argument('-e', '--explore',
                          action='store_true',
                          help='client to retrieve information from blockchains')
    features.add_argument('-d', '--disassemble',
                          action='store_true',
                          help='print text disassembly ')
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
    graph.add_argument('--onlystatic', action='store_true',
                       help='generate the CFG without stack emulation (fastest but less accurate)')
    graph.add_argument('--simplify', action='store_true',
                       help='generate a simplify CFG')
    graph.add_argument('--functions', action='store_true',
                       help='create subgraph for each function')
    graph.add_argument('--onlyfunction', type=str,
                       nargs="*",
                       default=[],
                       help='only generate the CFG for this list of function name')
    #graph.add_argument('--visualize',
    #                   help='direcly open the CFG file')
    #graph.add_argument('--format',
    #                   choices=['pdf', 'png', 'dot'],
    #                   default='pdf',
    #                   help='direcly open the CFG file')

    explorer = parser.add_argument_group('Explorer options')
    explorer.add_argument('--code',
                          help='get contract code',
                          metavar='CONTRACT_ADDRESS')
    explorer.add_argument('--tx',
                          help='get transaction information')
    #explorer.add_argument('--txdecode', action='store_true',
    #                      help='return important transaction information')
    explorer.add_argument('--blockid', type=int,
                          help='get block information using given block number',
                          metavar='BLOCK_NUMBER')
    explorer.add_argument('--blockhash',
                          help='get block information using given block hash',
                          metavar='BLOCK_HASH')
    explorer.add_argument('--infura',
                          help='Infura network choice',
                          choices=['mainnet', 'ropsten', 'infuranet', 'kovan', 'rinkeby'],
                          default='mainnet')
    explorer.add_argument('--rpc', help='custom RPC settings',
                          metavar='HOST:PORT')
    explorer.add_argument('--rpctls', action='store_false',
                          help='RPC connection over TLS')

    args = parser.parse_args()

    octo_bytecode = None
    octo_explorer = None
    octo_disasm = None
    octo_cfg = None

    # Explorer
    if args.explore or args.address:
        # user choose some explorer options
        if args.rpc:
            from octopus.platforms.ETH.explorer import EthereumExplorerRPC
            # parsing RPC HOST & PORT
            host, port = args.rpc.split(':')
            octo_explorer = EthereumExplorerRPC(host=host, port=port, tls=args.rpctls)
        else:
            from octopus.platforms.ETH.explorer import EthereumInfuraExplorer
            from octopus.platforms.ETH.explorer import (INFURA_MAINNET,
                                                        INFURA_ROPSTEN,
                                                        INFURA_INFURANET,
                                                        INFURA_KOVAN,
                                                        INFURA_RINKEBY)
            if args.infura == 'mainnet':
                network = INFURA_MAINNET
            if args.infura == 'ropsten':
                network = INFURA_ROPSTEN
            if args.infura == 'infuranet':
                network = INFURA_INFURANET
            if args.infura == 'kovan':
                network = INFURA_KOVAN
            if args.infura == 'rinkeby':
                network = INFURA_RINKEBY

            octo_explorer = EthereumInfuraExplorer(network=network)

        # process explorer related commands
        if args.code:
            print(octo_explorer.eth_getCode(args.code))
        elif args.tx:
            print(octo_explorer.get_transaction(args.tx))
        # elif args.txdecode:
        #    pass
        elif args.blockid:
            print(octo_explorer.get_block_by_number(args.blockid))
        elif args.blockhash:
            print(octo_explorer.get_block_by_hash(args.blockhash))

    # process input code
    if args.raw:
        octo_bytecode = args.raw
    elif args.file:
        octo_bytecode = ''.join([l.strip() for l in args.file if len(l.strip()) > 0])
    elif args.address:
        octo_bytecode = octo_explorer.eth_getCode(args.address)

    # Disassembly
    if args.disassemble:
        from octopus.platforms.ETH.disassembler import EthereumDisassembler

        # TODO add other r_format support
        octo_disasm = EthereumDisassembler()
        print(octo_disasm.disassemble(octo_bytecode, r_format='text'))

    # Control Flow Analysis
    elif args.cfg or args.ssa:
        from octopus.platforms.ETH.cfg import EthereumCFG
        from octopus.analysis.graph import CFGGraph

        if args.onlystatic and not args.ssa:
            octo_cfg = EthereumCFG(octo_bytecode, evm_analysis='static')
        else:
            octo_cfg = EthereumCFG(octo_bytecode)

        octo_graph = CFGGraph(octo_cfg)

        if args.functions or args.onlyfunction:
            octo_graph.view_functions(only_func_name=args.onlyfunction,
                                      simplify=args.simplify,
                                      ssa=args.ssa)
        else:
            octo_graph.view(simplify=args.simplify, ssa=args.ssa)

    # Call Flow Analysis
    elif args.call:
        error_print('Call Flow Analysis not yet supported')
    elif args.ssa:
        # already done
        pass
    elif args.explore:
        # already done
        pass
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
