from octopus.platforms.NEO.explorer import NeoExplorerRPC

# get list nodes here: http://monitor.cityofzion.io/
explorer = NeoExplorerRPC(host='pyrpc1.nodeneo.ch')

# get current number of block on the blockchain
print(explorer.getblockcount())
# 2534868

# get information on a contract
# lock smart contract address: d3cce84d0800172d09c88ccad61130611bd047a4
print(explorer.getcontractstate("d3cce84d0800172d09c88ccad61130611bd047a4"))
# {'author': 'Erik Zhang',
# 'code_version': '2.0',
# 'description': 'Lock 2.0',
# 'email': 'erik@neo.org',
# 'hash': '0xd3cce84d0800172d09c88ccad61130611bd047a4',
# 'name': 'Lock',
# 'parameters': ['Integer', 'PublicKey', 'Signature'],
# 'properties': {'dynamic_invoke': False, 'storage': False},
# 'returntype': 'Boolean',
# 'script': '56c56b6c766b00527ac46c766b51527ac46c766b52527ac4616168184e656f2e426c6f636b636861696e2e4765744865696768746168184e656f2e426c6f636b636861696e2e4765744865616465726c766b53527ac46c766b00c36c766b53c36168174e656f2e4865616465722e47657454696d657374616d70a06c766b54527ac46c766b54c3640e00006c766b55527ac4621a006c766b51c36c766b52c3617cac6c766b55527ac46203006c766b55c3616c7566',
# 'version': 0}