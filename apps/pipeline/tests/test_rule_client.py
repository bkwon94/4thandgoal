"""
The rule of the client files: each clients/<slug>/client.toml passes the check, and the exported schema is fresh.
The site build checks client.toml with the exported schema, so a stale file would let the two checks disagree.
"""
from pathlib import Path

import pytest

from cornerstone.client import check_schema_file, read_client_values

CLIENTS = Path(__file__).parents[3] / "clients"


@pytest.mark.parametrize("folder", sorted(p.parent for p in CLIENTS.glob("*/client.toml")), ids=lambda p: p.name)
def test_each_client_file_passes_the_check(folder):
    read_client_values(folder)


def test_the_exported_client_schema_is_fresh():
    check_schema_file()
