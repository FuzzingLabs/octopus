from octopus.arch.wasm.emulator import WasmSSAEmulatorEngine

# complete wasm module
file_name = "examples/wasm/samples/fib.wasm"

# read file
with open(file_name, 'rb') as f:
    raw = f.read()


# run the emulator for SSA
emul = WasmSSAEmulatorEngine(raw, 'fib')
emul.emulate()

# visualization of the cfg with SSA
emul.cfg.visualize(ssa=True)
