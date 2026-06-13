from __future__ import annotations

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pdm.backend.hooks import Context


def get_platform_tag() -> str:
    """
    Infer the wheel platform tag based on the current system.

    Returns platform tag like: manylinux_2_28_x86_64, macosx_11_0_arm64
    """
    machine = platform.machine().lower()
    system = platform.system().lower()

    # Determine architecture
    if any(arch in machine for arch in ("x86_64", "amd64")):
        arch = "x86_64"
    elif any(arch in machine for arch in ("arm64", "aarch64")):
        arch = "aarch64"
    else:
        message = f"Unknown architecture: {machine}"
        raise RuntimeError(message)

    # Determine platform tag based on system
    if system == "linux":
        if arch == "x86_64":
            return "manylinux_2_28_x86_64"
        elif arch == "aarch64":
            return "manylinux_2_28_aarch64"
    elif system == "darwin":
        if arch == "aarch64":
            return "macosx_11_0_arm64"
        elif arch == "x86_64":
            return "macosx_11_0_x86_64"

    message = f"Unsupported platform: {system} {arch}"
    raise RuntimeError(message)


def get_cpu_count():
    """Get number of CPUs for parallel compilation"""
    return str(os.cpu_count() or 1)


def build_from_source(build_dir: Path) -> None:
    """Build zstd binary from submodule source"""
    # Check if submodule exists
    zstd_src = Path("zstd")
    if not zstd_src.exists() or not (zstd_src / "Makefile").exists():
        message = (
            "zstd submodule not found. Run: git submodule update --init --recursive"
        )
        raise RuntimeError(message)

    print(f"Building zstd from source in {zstd_src}")
    print(f"Target platform: {platform.system()} {platform.machine()}")

    # Set reproducible build environment
    build_env = os.environ.copy()
    build_env["SOURCE_DATE_EPOCH"] = "0"
    build_env["TZ"] = "UTC"
    build_env["LANG"] = "C"

    # For macOS, set minimum deployment target
    if platform.system().lower() == "darwin":
        build_env["MACOSX_DEPLOYMENT_TARGET"] = "11.0"
        print("Set MACOSX_DEPLOYMENT_TARGET=11.0 for macOS compatibility")

    # Reproducible build flags
    reproducible_flags = (
        "-Wno-builtin-macro-redefined "
        '-D__DATE__="" '
        '-D__TIME__="" '
        '-D__TIMESTAMP__="" '
        f"-fdebug-prefix-map={zstd_src.absolute()}=."
    )

    cpu_count = get_cpu_count()

    # Build zstd
    print(f"Compiling with {cpu_count} parallel jobs...")
    subprocess.run(
        ["make", f"-j{cpu_count}", f"MOREFLAGS={reproducible_flags}"],
        cwd=zstd_src,
        env=build_env,
        check=True,
    )

    # Copy binary to build directory
    bin_dir = Path(build_dir, "bin")
    bin_dir.mkdir(parents=True, exist_ok=True)

    zstd_bin = bin_dir / "zstd"
    shutil.copy2(zstd_src / "programs" / "zstd", zstd_bin)
    zstd_bin.chmod(0o755)

    print(f"Built zstd binary: {zstd_bin}")

    # Verify the binary
    result = subprocess.run(
        [str(zstd_bin), "--version"], capture_output=True, text=True, check=True
    )
    print(f"Binary version: {result.stdout.strip()}")


def pdm_build_hook_enabled(context: Context):
    return context.target != "sdist"


def pdm_build_initialize(context: Context) -> None:
    # Infer platform tag
    platform_tag = get_platform_tag()
    print(f"Detected platform tag: {platform_tag}")

    setting = {
        "--python-tag": "py3",
        "--py-limited-api": "none",
        "--plat-name": platform_tag,
    }

    context.builder.config_settings = {**setting, **context.builder.config_settings}

    context.ensure_build_dir()

    # Build zstd binary from source
    build_from_source(context.build_dir)


def pdm_build_finalize(context: Context, artifact: Path) -> None:
    """Clean up build directory"""
    if context.build_dir.exists():
        shutil.rmtree(context.build_dir)

    print(f"Built wheel: {artifact.name}")
