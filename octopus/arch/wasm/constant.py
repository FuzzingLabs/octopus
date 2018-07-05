# https://github.com/WebAssembly/design/blob/master/BinaryEncoding.md#language-types
LANG_TYPE = {
    # Opcode, Type constructor
    -0x01: 'i32',
    -0x02: 'i64',
    -0x03: 'f32',
    -0x04: 'f64',
    -0x10: 'anyfunc',
    -0x20: 'func',
    -0x40: 'block_type'
}

KIND_TYPE = {
    0: 'function',
    1: 'table',
    2: 'memory',
    3: 'global',
}
