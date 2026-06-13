# zstd-bin

Precompiled zstd binaries distributed as Python wheels.

## Installation

```bash
pip install zstd-bin
```

After installation, the `zstd` command will be available in your PATH:

```bash
zstd --version
```

## Usage

This package provides the `zstd` command-line tool. All zstd commands work as expected:

```bash
# Compress a file
zstd file.txt

# Decompress
zstd -d file.txt.zst

# View help
zstd --help
```

## Supported Platforms

- Linux x86_64 (manylinux_2_28, glibc 2.28+)
- Linux aarch64 (manylinux_2_28, glibc 2.28+)
- macOS arm64 (macOS 11.0+)
- macOS x86_64 (macOS 11.0+)

## Building from Source

This package automatically compiles zstd from source when building wheels.

To build locally:

```bash
# Clone with submodules
git clone --recurse-submodules https://github.com/czudf/zstd-bin

# Or if already cloned, initialize submodules
git submodule update --init --recursive

# Install uv (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Build wheel for your platform (automatically compiles zstd from source)
uv build --wheel

# Test installation
uv venv .venv
uv pip install --no-index -f dist/ zstd-bin
.venv/bin/zstd --version
```

The build process:
1. Automatically detects your platform (Linux/macOS, x86_64/aarch64)
2. Compiles zstd from the included git submodule (zstd/)
3. Creates a platform-specific wheel with the compiled binary

## License

This package distributes zstd binaries which are licensed under BSD-3-Clause.
See https://github.com/facebook/zstd for the original zstd project.

## Acknowledgments

This project was inspired by and learned from [pip-binary-factory](https://github.com/Bing-su/pip-binary-factory), which provides an excellent framework for distributing precompiled binaries via Python wheels.

## Repository

https://github.com/czudf/zstd-bin
