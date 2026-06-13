import shutil
import subprocess
import sys

if __name__ == "__main__":
    zstd = shutil.which("zstd")
    if zstd is None:
        msg = "Not found 'zstd' in $PATH"
        raise RuntimeError(msg)

    subprocess.run([zstd, *sys.argv[1:]])
