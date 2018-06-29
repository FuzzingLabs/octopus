echo 'test BTC Disassembler'
python3 -m unittest octopus/tests/platforms/BTC/test_disassembler.py

echo 'test NEO Disassembler'
python3 -m unittest octopus/tests/platforms/NEO/test_disassembler.py
echo 'test NEO Cfg recovery'
python3 -m unittest octopus/tests/platforms/NEO/test_cfg.py

echo 'test ETH Disassembler'
python3 -m unittest octopus/tests/platforms/ETH/test_disassembler.py
echo 'test ETH Cfg recovery'
python3 -m unittest octopus/tests/platforms/ETH/test_cfg.py

