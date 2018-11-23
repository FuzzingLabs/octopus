echo '[*] NEO Disassembler [*]'
python3 -m unittest NEO/test_disassembler.py
echo '[*] NEO ControlFlowGraph analysis [*]'
python3 -m unittest NEO/test_cfg.py