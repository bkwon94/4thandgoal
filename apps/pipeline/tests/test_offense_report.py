"""
Checks the shape that rule_report prints for an offense, byte for byte.
The shape is in docs/adr/0014-the-rules-are-checks.md, "The report of an offense".
"""
from rule_report import Offense, report

UPWARD = Offense(
    path="src/cornerstone/waiver.py",
    line=12,
    rule_id="layers/upward-import",
    what="cornerstone.waiver imports cornerstone.writer.",
    rule="a module imports only from its own layer or a lower one",
    adr="docs/adr/0010-six-layers-import-downward-only.md",
    fix="move the shared name to a module in a lower layer, or move cornerstone.waiver up in LAYER_OF.",
)


def test_one_offense_prints_in_the_house_shape():
    assert report([UPWARD]) == (
        "1 offense.\n"
        "\n"
        "src/cornerstone/waiver.py:12  layers/upward-import\n"
        "  cornerstone.waiver imports cornerstone.writer.\n"
        "  Rule: a module imports only from its own layer or a lower one "
        "(docs/adr/0010-six-layers-import-downward-only.md).\n"
        "  Fix: move the shared name to a module in a lower layer, or move cornerstone.waiver up in LAYER_OF.")


def test_two_offenses_start_with_the_count_and_have_a_blank_line_between():
    text = report([UPWARD, UPWARD])
    assert text.startswith("2 offenses.\n\nsrc/cornerstone/waiver.py:12  layers/upward-import\n")
    assert "LAYER_OF.\n\nsrc/cornerstone/waiver.py:12" in text
