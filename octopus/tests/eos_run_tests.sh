echo '[*] EOS Disassembler [*]'
python3 -m unittest octopus/tests/EOS/test_disassembler.py
echo '[*] EOS CallGraph analysis [*]'
python3 -m unittest octopus/tests/EOS/test_callgraph.py