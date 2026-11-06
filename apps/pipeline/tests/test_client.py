"""
Tests for the check of the client files: the kernel keys of clients/<slug>/client.toml, each [values.<package>] table,
and the exported JSON Schemas. Each bad file fails with a plain message that names the file and the bad value.
"""
import json
import shutil
from pathlib import Path
from typing import get_args

import pytest

from analyzer.values import AnalyzerValues
from cornerstone.value_models import VALUE_MODELS
from league.client import (
    CLIENT_SCHEMA,
    ClientError,
    ClientValues,
    PackageName,
    check_schema_file,
    read_client_values,
    schema_file,
)
from league.values import LeagueValues
from midseason.values import MidseasonValues
from week.values import WeekValues

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
    values = read_client_values(CPC, VALUE_MODELS)
    assert values.packages == ["week", "rankings", "managers", "analyzer", "midseason", "sim"]
    assert values.timezone == "America/New_York"
    assert values.usage_code == "cpcfantasy"
    assert values.seasons[2026].provider == "sleeper"
    assert values.seasons[2026].league_id == "1386167364424318976"
    assert values.package(AnalyzerValues).finder is False
    assert values.package(LeagueValues).chart == "1QB0.5PPR4pt"
    assert [item.package or item.page for item in values.menu.items] == [
        "home", "week", "rankings", "managers", "analyzer"]


def test_a_client_with_no_chart_value_has_no_chart(tmp_path):
    # The default of the league package is no chart, and then each chart value is 0.
    folder = _copy(tmp_path, '[values.league]\nchart = "1QB0.5PPR4pt"\n', "")
    assert read_client_values(folder, VALUE_MODELS).package(LeagueValues).chart is None


def test_an_unknown_key_fails_with_the_key_and_the_file(tmp_path):
    # AT-20: a typo never passes as a default.
    folder = _copy(tmp_path, "finder = false", "finder = false\nfinderr = true")
    with pytest.raises(ClientError) as err:
        read_client_values(folder, VALUE_MODELS)
    assert "- values.analyzer.finderr: is not a known key" in str(err.value)
    assert str(folder / "client.toml") in str(err.value)


def test_a_table_of_a_package_off_the_list_fails_with_the_table(tmp_path):
    folder = _copy(tmp_path, "[values.analyzer]", "[values.waiver]\n\n[values.analyzer]")
    with pytest.raises(ClientError) as err:
        read_client_values(folder, VALUE_MODELS)
    assert "- values.waiver: names a package that is not in the package list" in str(err.value)
    assert str(folder / "client.toml") in str(err.value)


def test_a_package_of_the_list_with_no_table_takes_the_defaults_of_its_model():
    values = read_client_values(CPC, VALUE_MODELS)
    assert values.package(WeekValues) == WeekValues()


def test_the_pipeline_has_one_values_model_for_each_package():
    assert sorted(model.package for model in VALUE_MODELS) == sorted(["league", *get_args(PackageName)])


def test_a_menu_item_for_an_omitted_package_fails_with_the_item_and_the_package(tmp_path):
    # AT-21: the menu names only a package of the list.
    folder = _copy(tmp_path, '{ package = "week" },', '{ package = "week" },\n  { package = "waiver" },')
    with pytest.raises(ClientError) as err:
        read_client_values(folder, VALUE_MODELS)
    assert "waiver" in str(err.value)
    assert "menu" in str(err.value)


def test_a_client_with_midseason_and_no_sim_fails_and_names_sim(tmp_path):
    # AT-48: the report ends on the sim, so a client that takes midseason takes sim too.
    folder = _copy(tmp_path, 'packages = ["week", "rankings", "managers", "analyzer", "midseason", "sim"]',
                   'packages = ["week", "rankings", "managers", "analyzer", "midseason"]')
    with pytest.raises(ClientError) as err:
        read_client_values(folder, VALUE_MODELS)
    assert "- The midseason package needs the sim package. Add sim to the package list." in str(err.value)
    assert str(folder / "client.toml") in str(err.value)


def test_a_client_with_midseason_and_sim_passes(tmp_path):
    folder = _copy(tmp_path, 'packages = ["week", "rankings", "managers", "analyzer", "midseason", "sim"]',
                   'packages = ["week", "rankings", "managers", "analyzer", "sim", "midseason"]')
    assert read_client_values(folder, VALUE_MODELS).packages[-2:] == ["sim", "midseason"]


def test_a_roast_outside_the_four_levels_fails_and_names_them(tmp_path):
    # AT-62: the roast setting of midseason takes four levels only.
    folder = _copy(tmp_path, "[values.analyzer]", '[values.midseason]\nroast = "nuclear"\n\n[values.analyzer]')
    with pytest.raises(ClientError) as err:
        read_client_values(folder, VALUE_MODELS)
    message = str(err.value)
    assert "values.midseason.roast" in message
    for level in ("'off'", "'warm'", "'hot'", "'savage'"):
        assert level in message


def test_a_client_with_no_roast_value_takes_savage(tmp_path):
    # AT-41: savage is the default of the roast setting.
    assert read_client_values(CPC, VALUE_MODELS).package(MidseasonValues).roast == "savage"


def test_a_missing_timezone_fails_with_the_key(tmp_path):
    folder = _copy(tmp_path, 'timezone = "America/New_York"\n', "")
    with pytest.raises(ClientError, match="timezone"):
        read_client_values(folder, VALUE_MODELS)


def test_an_unknown_timezone_fails_with_the_value(tmp_path):
    folder = _copy(tmp_path, "America/New_York", "America/Nowhere")
    with pytest.raises(ClientError, match="America/Nowhere"):
        read_client_values(folder, VALUE_MODELS)


def test_a_menu_layout_fails_because_the_look_owns_the_navigation(tmp_path):
    folder = _copy(tmp_path, "[menu]\n", '[menu]\nlayout = "hamburger"\n')
    with pytest.raises(ClientError, match="layout"):
        read_client_values(folder, VALUE_MODELS)


def test_a_client_with_no_seasons_fails(tmp_path):
    folder = _copy(tmp_path, '[seasons.2026]\nprovider = "sleeper"\nleague_id = "1386167364424318976"\n', "")
    with pytest.raises(ClientError, match="seasons"):
        read_client_values(folder, VALUE_MODELS)


def test_a_file_that_is_not_toml_fails_with_the_file(tmp_path):
    folder = _copy(tmp_path, "[menu]", "[menu")
    with pytest.raises(ClientError) as err:
        read_client_values(folder, VALUE_MODELS)
    assert str(folder / "client.toml") in str(err.value)


def test_a_missing_client_folder_names_the_slug_folder(tmp_path):
    with pytest.raises(ClientError, match="nope"):
        read_client_values(tmp_path / "clients" / "nope", VALUE_MODELS)


def test_the_kernel_schema_forbids_an_unknown_key_and_each_package_schema_sits_in_its_package():
    assert ClientValues.model_json_schema()["additionalProperties"] is False
    analyzer = schema_file(AnalyzerValues)
    assert analyzer.parts[-6:] == ("packages", "analyzer", "python", "src", "analyzer", "values.schema.json")
    assert "finder" in analyzer.read_text(encoding="utf-8")


def test_a_stale_schema_file_fails_with_the_file_and_the_command(tmp_path, monkeypatch):
    # The kernel schema of league: the site and the pipeline check against the same rules, so a stale export fails.
    stale = tmp_path / "client.schema.json"
    shutil.copy(CLIENT_SCHEMA, stale)
    data = json.loads(stale.read_text(encoding="utf-8"))
    data["title"] = "Old"
    stale.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ClientError) as err:
        check_schema_file(ClientValues, stale)
    assert str(stale) in str(err.value)
    assert "make schema in packages/league/python" in str(err.value)


def test_a_new_analyzer_value_with_no_export_names_the_stale_schema_file_of_analyzer():
    # AT-22: a new package value in the model of analyzer, with no new export of its JSON Schema.
    class AnalyzerWithNewValue(AnalyzerValues):
        reasons: bool = True

    AnalyzerWithNewValue.__module__ = AnalyzerValues.__module__
    with pytest.raises(ClientError) as err:
        check_schema_file(AnalyzerWithNewValue, schema_file(AnalyzerValues))
    assert str(schema_file(AnalyzerValues)) in str(err.value)
    assert "of analyzer is stale" in str(err.value)
    assert "make schema in packages/analyzer/python" in str(err.value)


def test_the_model_rejects_an_extra_top_level_key():
    with pytest.raises(ClientError, match="theme"):
        ClientValues.from_toml_text('packages = []\ntimezone = "UTC"\ntheme = "dark"\n[seasons.2026]\n'
                                    'provider = "sleeper"\nleague_id = "1"\n', Path("client.toml"),
                                    VALUE_MODELS)
