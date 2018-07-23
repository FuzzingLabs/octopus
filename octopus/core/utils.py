
def bytecode_to_bytes(bytecode):
    if str(bytecode).startswith("0x"):
        bytecode = str(bytecode)[2:]

    try:
        bytecode = bytes.fromhex(bytecode)
    except TypeError:
        pass
    return bytecode
