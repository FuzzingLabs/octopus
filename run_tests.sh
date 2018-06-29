echo '[*] BTC tests'
echo '[*] Disassembler [*]'
python3 -m unittest octopus/tests/platforms/BTC/test_disassembler.py

echo '[*] NEO tests'
echo '[*] Disassembler [*]'
python3 -m unittest octopus/tests/platforms/NEO/test_disassembler.py
echo '[*] CFG recovery [*]'
python3 -m unittest octopus/tests/platforms/NEO/test_cfg.py

echo '[*] ETH tests'
echo '[*] Explorer [*]'
python3 -m unittest octopus/tests/platforms/ETH/test_explorer.py
echo '[*] Disassembler [*]'
python3 -m unittest octopus/tests/platforms/ETH/test_disassembler.py
echo '[*] CFG recovery [*]'
python3 -m unittest octopus/tests/platforms/ETH/test_cfg.py

