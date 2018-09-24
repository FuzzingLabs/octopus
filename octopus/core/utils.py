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
    # already bytes or bytearray
    except TypeError:
        pass
    return bytecode


def search_in_list_of_dict(string_to_search, target_list, key_dict):
    return list(filter(lambda elem: str(string_to_search) in str(elem[key_dict]), target_list))
