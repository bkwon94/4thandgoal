"""
Write a file so that a stopped write never leaves a half file.
Every cache and state file in the project goes through this one function.
"""
import os
import tempfile
from pathlib import Path


def write_bytes_atomic(path: Path, body: bytes) -> None:
    # A temp file then a replace, so a stopped write never leaves a half file that the next run reads.
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(body)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise
