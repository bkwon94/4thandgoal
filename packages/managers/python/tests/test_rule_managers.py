"""
Runs the rule tests of the pipeline on the managers package: the suppression comments and the READMEs.
The layer rule of tests/test_layers.py in the pipeline reads the managers package too. See ADR 0010 and ADR 0014.
"""
from pathlib import Path

import test_rule_readmes as readmes
import test_rule_suppressions as suppressions
from rule_report import report

ROOT = Path(__file__).resolve().parent.parent
# The repo root holds packages/, which the package README rule reads.
REPO = ROOT.parents[2]

# The allow list of the managers package, in the shape of the allow list of the pipeline. The key is the path from
# packages/managers/python. The package silences no rule, so the list is empty.
ALLOW: dict[tuple[str, str], str] = {}


def test_no_comment_in_the_managers_package_silences_a_rule():
    offenses = suppressions._comment_offenses(ROOT, ALLOW)
    assert not offenses, report(offenses)


def test_each_readme_of_the_managers_package_has_the_three_headings_and_is_short():
    # The package README sits at packages/managers/README.md, so the folder src/managers holds none of its own.
    offenses = readmes._heading_offenses(ROOT) + readmes._length_offenses(ROOT)
    assert not offenses, report(offenses)


def test_the_managers_package_has_a_readme_with_the_three_headings():
    offenses = [offense for offense in readmes._package_readme_offenses(REPO)
                if offense.path.startswith("packages/managers")]
    assert not offenses, report(offenses)
