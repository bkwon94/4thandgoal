"""
The rule of the client files: each clients/<slug>/client.toml passes the check, and each exported schema is fresh.
The site build checks client.toml with the exported schemas, so a stale file would let the two checks disagree.
"""
from pathlib import Path

import pytest

from cornerstone.value_models import VALUE_MODELS
from league.client import check_schema_files, read_client_values

CLIENTS = Path(__file__).parents[3] / "clients"


@pytest.mark.parametrize("folder", sorted(p.parent for p in CLIENTS.glob("*/client.toml")), ids=lambda p: p.name)
def test_each_client_file_passes_the_check(folder):
    read_client_values(folder, VALUE_MODELS)


def test_each_exported_schema_is_fresh():
    # The kernel schema of league and the values schema of each package.
    check_schema_files(VALUE_MODELS)
