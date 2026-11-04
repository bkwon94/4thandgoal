"""
Runs the rule tests of the pipeline on the API app: the import layers, the suppression comments, and the READMEs.
The rules live in the pipeline tests, and each one takes the root it reads. See ADR 0010 and ADR 0014.
"""
from pathlib import Path

import test_layers as layers
import test_rule_readmes as readmes
import test_rule_suppressions as suppressions
from rule_report import report

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
MARKER = suppressions.MARKER

# The allow list of the API, in the shape of the allow list of the pipeline. The key is the path from the API app.
ALLOW: dict[tuple[str, str], str] = {
    ("src/cornerstone_api/app.py",
     f"except Exception as error:  # {MARKER}: BLE001 - the app keeps running after a failed refresh"):
        "the app keeps running after a failed refresh",
    ("src/cornerstone_api/sources.py",
     f"read_chart: ChartReader = partial(chart_values, read=claude_reader(parse_call))  # {MARKER}: RUF009"):
        "one shared partial holds no state that a call changes",
}


def test_the_api_imports_only_from_layer_write_or_a_lower_one():
    offenses = layers._import_offenses(layers.SRC, SRC)
    assert not offenses, report(offenses)


def test_the_rule_reads_each_module_of_the_api():
    modules = layers._modules(layers.SRC, SRC)
    assert {"cornerstone_api.app", "cornerstone_api.sources"} <= set(modules)


def test_no_comment_in_the_api_silences_a_rule():
    offenses = suppressions._comment_offenses(ROOT, ALLOW)
    assert not offenses, report(offenses)


def test_the_allow_list_of_the_api_names_only_lines_that_exist():
    found = {(path, text) for path, _, text in suppressions._suppressions(ROOT)}
    assert [key for key in ALLOW if key not in found] == []


def test_each_package_folder_of_the_api_has_a_readme_with_the_three_headings():
    offenses = readmes._missing_offenses(ROOT) + readmes._heading_offenses(ROOT) + readmes._length_offenses(ROOT)
    assert not offenses, report(offenses)
