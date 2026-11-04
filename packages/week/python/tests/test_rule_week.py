"""
Runs the rule tests of the pipeline on the week package: the suppression comments and the READMEs.
The layer rule of tests/test_layers.py in the pipeline reads the week package too. See ADR 0010 and ADR 0014.
"""
from pathlib import Path

import test_rule_readmes as readmes
import test_rule_suppressions as suppressions
from rule_report import report

ROOT = Path(__file__).resolve().parent.parent
MARKER = suppressions.MARKER

# The allow list of the week package, in the shape of the allow list of the pipeline. The key is the path from
# packages/week/python.
ALLOW: dict[tuple[str, str], str] = {
    ("src/week/page.py",
     f"except Exception as exc:  # {MARKER}: BLE001 - a build never stops on one avatar"):
        "a build never stops on one avatar",
}


def test_no_comment_in_the_week_package_silences_a_rule():
    offenses = suppressions._comment_offenses(ROOT, ALLOW)
    assert not offenses, report(offenses)


def test_the_allow_list_of_the_week_package_names_only_lines_that_exist():
    found = {(path, text) for path, _, text in suppressions._suppressions(ROOT)}
    assert [key for key in ALLOW if key not in found] == []


def test_each_readme_of_the_week_package_has_the_three_headings_and_is_short():
    # The package README sits at packages/week/README.md. The folder src/week/sheet holds its own README too.
    offenses = readmes._heading_offenses(ROOT) + readmes._length_offenses(ROOT)
    assert not offenses, report(offenses)


def test_the_week_package_has_a_readme_with_the_three_headings():
    offenses = [offense for offense in readmes._package_readme_offenses(ROOT.parents[1])
                if offense.path.startswith("packages/week")]
    assert not offenses, report(offenses)
