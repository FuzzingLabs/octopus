echo '[*] EOS Disassembler [*]'
python3 -m unittest EOS/test_disassembler.py
echo '[*] EOS CallGraph analysis [*]'
python3 -m unittest EOS/test_callgraph.py