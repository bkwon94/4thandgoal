"""
Tests for the check of the client files: the values of clients/<slug>/client.toml and their exported JSON Schema.
Each bad file fails with a plain message that names the file and the bad value.
"""
import json
import shutil
from pathlib import Path

import pytest

from cornerstone.client import CLIENT_SCHEMA, ClientError, ClientValues, client_schema, read_client_values

ROOT = Path(__file__).parents[3]
CPC = ROOT / "clients" / "cpc"


def _copy(tmp_path: Path, old: str, new: str) -> Path:
    """A copy of the CPC client folder with one text change in client.toml."""
    folder = tmp_path / "clients" / "cpc"
    folder.mkdir(parents=True)
    text = (CPC / "client.toml").read_text(encoding="utf-8")
    assert old in text
    (folder / "client.toml").write_text(text.replace(old, new), encoding="utf-8")
    return folder


def test_the_cpc_client_reads_the_values_of_the_spec():
    values = read_client_values(CPC)
    assert values.packages == ["week", "rankings", "managers", "analyzer"]
    assert values.timezone == "America/New_York"
    assert values.usage_code == "cpcfantasy"
    assert values.seasons[2026].provider == "sleeper"
    assert values.seasons[2026].league_id == "1386167364424318976"
    assert values.values.analyzer.finder is False
    assert values.values.league.chart is None
    assert values.menu.layout == "hamburger"
    assert [item.package or item.page for item in values.menu.items] == [
        "home", "week", "rankings", "managers", "analyzer"]


def test_an_unknown_key_fails_with_the_key_and_the_file(tmp_path):
    # AT-20: a typo never passes as a default.
    folder = _copy(tmp_path, "finder = false", "finder = false\nfinderr = true")
    with pytest.raises(ClientError) as err:
        read_client_values(folder)
    assert "finderr" in str(err.value)
    assert str(folder / "client.toml") in str(err.value)


def test_a_menu_item_for_an_omitted_package_fails_with_the_item_and_the_package(tmp_path):
    # AT-21: the menu names only a package of the list.
    folder = _copy(tmp_path, '{ package = "week" },', '{ package = "week" },\n  { package = "waiver" },')
    with pytest.raises(ClientError) as err:
        read_client_values(folder)
    assert "waiver" in str(err.value)
    assert "menu" in str(err.value)


def test_a_missing_timezone_fails_with_the_key(tmp_path):
    folder = _copy(tmp_path, 'timezone = "America/New_York"\n', "")
    with pytest.raises(ClientError, match="timezone"):
        read_client_values(folder)


def test_an_unknown_timezone_fails_with_the_value(tmp_path):
    folder = _copy(tmp_path, "America/New_York", "America/Nowhere")
    with pytest.raises(ClientError, match="America/Nowhere"):
        read_client_values(folder)


def test_a_bad_layout_fails_with_the_value(tmp_path):
    folder = _copy(tmp_path, 'layout = "hamburger"', 'layout = "drawer"')
    with pytest.raises(ClientError, match="layout"):
        read_client_values(folder)


def test_a_client_with_no_seasons_fails(tmp_path):
    folder = _copy(tmp_path, '[seasons.2026]\nprovider = "sleeper"\nleague_id = "1386167364424318976"\n', "")
    with pytest.raises(ClientError, match="seasons"):
        read_client_values(folder)


def test_a_file_that_is_not_toml_fails_with_the_file(tmp_path):
    folder = _copy(tmp_path, "[menu]", "[menu")
    with pytest.raises(ClientError) as err:
        read_client_values(folder)
    assert str(folder / "client.toml") in str(err.value)


def test_a_missing_client_folder_names_the_slug_folder(tmp_path):
    with pytest.raises(ClientError, match="nope"):
        read_client_values(tmp_path / "clients" / "nope")


def test_a_menu_with_no_items_takes_the_package_list_in_order(tmp_path):
    folder = _copy(tmp_path, "[menu]", "[unused]")
    text = (folder / "client.toml").read_text(encoding="utf-8")
    (folder / "client.toml").write_text(text[:text.index("[unused]")] + '[menu]\nlayout = "bar"\n', encoding="utf-8")
    values = read_client_values(folder)
    assert [item.package for item in values.menu_items] == values.packages


def test_the_exported_schema_names_each_package_value():
    schema = client_schema()
    assert schema["additionalProperties"] is False
    assert "finder" in json.dumps(schema)


def test_a_stale_schema_file_fails_with_the_file_and_the_command(tmp_path, monkeypatch):
    # AT-22: the site and the pipeline check against the same rules, so a stale export fails.
    from cornerstone import client as client_module
    stale = tmp_path / "client.schema.json"
    shutil.copy(CLIENT_SCHEMA, stale)
    data = json.loads(stale.read_text(encoding="utf-8"))
    data["title"] = "Old"
    stale.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ClientError) as err:
        client_module.check_schema_file(stale)
    assert str(stale) in str(err.value)
    assert "make schema" in str(err.value)


def test_the_model_rejects_an_extra_top_level_key():
    with pytest.raises(ClientError, match="theme"):
        ClientValues.from_toml_text('packages = []\ntimezone = "UTC"\ntheme = "dark"\n[seasons.2026]\n'
                                    'provider = "sleeper"\nleague_id = "1"\n', Path("client.toml"))
