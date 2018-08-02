from binascii import unhexlify


def bytecode_to_bytes(bytecode):
    if str(bytecode).startswith("0x"):
        bytecode = bytecode[2:]

    try:
        # python > 2.7
        bytecode = bytes.fromhex(bytecode)
    except AttributeError:
        # python <= 2.7
        try:
            bytecode = bytecode.decode("hex")
        except TypeError:
            # last chance
            try:
                bytecode = unhexlify(bytecode)
            except:
                pass
    return bytecode
