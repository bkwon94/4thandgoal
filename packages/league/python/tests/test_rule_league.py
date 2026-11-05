"""
Runs the rule tests of the pipeline on the league package: the suppression comments and the READMEs.
The layer rule of tests/test_layers.py in the pipeline reads the league package too. See ADR 0010 and ADR 0014.
"""
from pathlib import Path

import test_rule_readmes as readmes
import test_rule_suppressions as suppressions
from rule_report import report

ROOT = Path(__file__).resolve().parent.parent
MARKER = suppressions.MARKER

# The allow list of the league package, in the shape of the allow list of the pipeline. The key is the path from
# packages/league/python.
ALLOW: dict[tuple[str, str], str] = {
    ("src/league/live.py",
     f"except Exception as error:  # {MARKER}: BLE001 - the docstring says why: no error may stop the service"):
        "the docstring says why: no error may stop the service",
}


def test_no_comment_in_the_league_package_silences_a_rule():
    offenses = suppressions._comment_offenses(ROOT, ALLOW)
    assert not offenses, report(offenses)


def test_the_allow_list_of_the_league_package_names_only_lines_that_exist():
    found = {(path, text) for path, _, text in suppressions._suppressions(ROOT)}
    assert [key for key in ALLOW if key not in found] == []


def test_each_readme_of_the_league_package_has_the_three_headings_and_is_short():
    # The package README sits at packages/league/README.md, so the folder src/league holds none of its own.
    offenses = readmes._heading_offenses(ROOT) + readmes._length_offenses(ROOT)
    assert not offenses, report(offenses)
