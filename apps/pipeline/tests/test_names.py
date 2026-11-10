"""
Tests for the player name helpers: the last name of a full name and the short name in a trend reason.
They use plain names, so no test reads a fixture.
"""
from types import SimpleNamespace

from analyzer.measures import _short_names
from facts.names import last_name


def _snapshot(names):
    return SimpleNamespace(players={pid: SimpleNamespace(name=name) for pid, name in names.items()})


def test_last_name_keeps_a_particle_before_the_last_word():
    assert last_name("Amon-Ra St. Brown") == "St. Brown"
    assert last_name("Lukas Van Ness") == "Van Ness"
    assert last_name("Gerhard de Beer") == "de Beer"
    assert last_name("Zach Von Rosenberg") == "Von Rosenberg"


def test_last_name_is_one_word_without_a_particle():
    assert last_name("Josh Jacobs") == "Jacobs"
    assert last_name("Marvin Harrison Jr.") == "Harrison"


def test_a_particle_as_a_first_name_is_not_part_of_the_last_name():
    # "Van" is a first name here, so the last name is one word.
    assert last_name("Van Jefferson") == "Jefferson"


def test_a_short_last_word_after_a_particle_still_has_no_last_name():
    # The particle does not lift the gate on a short last word.
    assert last_name("Kyle Van Noy") is None


def test_two_st_browns_in_one_trade_both_show_in_full():
    names = _short_names(_snapshot({"1": "Amon-Ra St. Brown", "2": "Equanimeous St. Brown", "3": "Josh Jacobs"}),
                         ["1", "2", "3"])
    assert names == {"1": "Amon-Ra St. Brown", "2": "Equanimeous St. Brown", "3": "Jacobs"}


def test_one_st_brown_in_a_trade_shortens_to_st_brown():
    assert _short_names(_snapshot({"1": "Amon-Ra St. Brown"}), ["1"]) == {"1": "St. Brown"}
