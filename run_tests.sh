echo 'test BTC disassembler'
python3 -m unittest octopus/tests/platforms/BTC/test_disassembler.py

echo 'test NEO disassembler'
python3 -m unittest octopus/tests/platforms/NEO/test_disassembler.py
echo 'test NEO cfg'
python3 -m unittest octopus/tests/platforms/NEO/test_cfg.py

echo 'test ETH disassembler'
python3 -m unittest octopus/tests/platforms/ETH/test_disassembler.py
echo 'test ETH cfg'
python3 -m unittest octopus/tests/platforms/ETH/test_cfg.py

