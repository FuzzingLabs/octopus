echo '[*] WebAssembly Disassembler [*]'
python3 -m unittest wasm/test_disassembler.py
echo '[*] WebAssembly ControlFlowGraph & CallGraph analysis [*]'
python3 -m unittest wasm/test_cfg.py