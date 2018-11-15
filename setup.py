from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="octopus",
    version="0.3.3",
    author="QuoScient",
    license='MIT',
    description="Security analysis framework for WebAssembly module (wasm) and Blockchain Smart Contract (BTC/ETH/EOS/NEO).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/quoscient/octopus",
    keywords='disassembler security webassembly ethereum eos neo',
    packages=find_packages(),
    classifiers=(
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Disassemblers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ),

    install_requires=[
        'z3-solver>=4.5',
        'requests>=2.18.4',
        'graphviz>=0.8.3',
        'wasm>=1.1'
    ],

    python_requires='>=3.5',

    package_data={
        'octopus.arch.evm': ['*.json'],
        'octopus.arch.wasm.signatures': ['*.json']
    },

    entry_points={
        'console_scripts': [
            'octopus_eth_evm = octopus.octopus_eth_evm:main',
            'octopus_wasm = octopus.octopus_wasm:main',
        ],

    },
)
