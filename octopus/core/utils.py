from binascii import unhexlify


def bytecode_to_bytes(bytecode):
    if str(bytecode).startswith("0x"):
        bytecode = bytecode[2:]

    try:
        bytecode = bytes.fromhex(bytecode)
    except TypeError:
        try:
            bytecode = unhexlify(bytecode)
        except:
            pass
    return bytecode
