"""
Tests of the atomic write helper.
A failed write leaves neither the target file nor a temp file.
"""
import os
from pathlib import Path

import pytest

from league.files import write_bytes_atomic


def test_file_holds_the_body(tmp_path: Path):
    target = tmp_path / "out.bin"
    write_bytes_atomic(target, b"hello")
    assert target.read_bytes() == b"hello"


def test_failed_write_leaves_no_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def broken_replace(src, dst):
        raise OSError("disk gone")

    monkeypatch.setattr(os, "replace", broken_replace)
    with pytest.raises(OSError):
        write_bytes_atomic(tmp_path / "out.bin", b"hello")
    assert list(tmp_path.iterdir()) == []
