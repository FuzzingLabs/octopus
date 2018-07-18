echo '[*] BTC Disassembler [*]'
python3 -m unittest octopus/tests/platforms/BTC/test_disassembler.py

echo '[*] NEO Disassembler [*]'
python3 -m unittest octopus/tests/platforms/NEO/test_disassembler.py
echo '[*] NEO ControlFlowGraph analysis [*]'
python3 -m unittest octopus/tests/platforms/NEO/test_cfg.py

# echo '[*] ETH Explorer [*]'
# python3 -m unittest octopus/tests/platforms/ETH/test_explorer.py
echo '[*] ETH Disassembler [*]'
python3 -m unittest octopus/tests/platforms/ETH/test_disassembler.py
echo '[*] ETH ControlFlowGraph analysis [*]'
python3 -m unittest octopus/tests/platforms/ETH/test_cfg.py

echo '[*] EOS Disassembler [*]'
python3 -m unittest octopus/tests/platforms/EOS/test_disassembler.py
echo '[*] EOS CallGraph analysis [*]'
python3 -m unittest octopus/tests/platforms/EOS/test_callgraph.py

echo '[*] WebAssembly ControlFlowGraph & CallGraph analysis [*]'
python3 -m unittest octopus/tests/arch/wasm/test_cfg.py