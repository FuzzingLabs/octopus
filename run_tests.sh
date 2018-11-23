echo '[*] BTC Disassembler [*]'
python3 -m unittest octopus/tests/BTC/test_disassembler.py

echo '[*] NEO Disassembler [*]'
python3 -m unittest octopus/tests/NEO/test_disassembler.py
echo '[*] NEO ControlFlowGraph analysis [*]'
python3 -m unittest octopus/tests/NEO/test_cfg.py

# echo '[*] ETH Explorer [*]'
# python3 -m unittest octopus/tests/ETH/test_explorer.py
echo '[*] ETH Disassembler [*]'
python3 -m unittest octopus/tests/ETH/test_disassembler.py
echo '[*] ETH ControlFlowGraph analysis [*]'
python3 -m unittest octopus/tests/ETH/test_cfg.py

echo '[*] EOS Disassembler [*]'
python3 -m unittest octopus/tests/EOS/test_disassembler.py
echo '[*] EOS CallGraph analysis [*]'
python3 -m unittest octopus/tests/EOS/test_callgraph.py

echo '[*] WebAssembly Disassembler [*]'
python3 -m unittest octopus/tests/WASM/test_disassembler.py
echo '[*] WebAssembly ControlFlowGraph & CallGraph analysis [*]'
python3 -m unittest octopus/tests/WASM/test_cfg.py