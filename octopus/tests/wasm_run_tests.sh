echo '[*] WebAssembly Disassembler [*]'
python3 -m unittest WASM/test_disassembler.py
echo '[*] WebAssembly ControlFlowGraph & CallGraph analysis [*]'
python3 -m unittest WASM/test_cfg.py