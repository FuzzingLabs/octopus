echo '[*] WebAssembly Disassembler [*]'
python3 -m unittest octopus/tests/wasm/test_disassembler.py
echo '[*] WebAssembly ControlFlowGraph & CallGraph analysis [*]'
python3 -m unittest octopus/tests/wasm/test_cfg.py