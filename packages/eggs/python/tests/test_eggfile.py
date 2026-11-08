"""
Tests for the egg file: a bad file raises EggFileError with the file name and the problem.
Each test writes a real temp file.
"""
import pytest

from eggs.eggfile import EggFileError, Spot, append_spots, read_spots

GOOD = '[[eggs]]\nweek = 8\npage = "/a/"\ntarget = "t"\naction = "tap2"\nconfirmed = true\n'


def _file(tmp_path, text):
    path = tmp_path / "2026.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_good_file_reads_its_spots(tmp_path):
    assert [spot.page for spot in read_spots(_file(tmp_path, GOOD))] == ["/a/"]


def test_a_file_that_is_not_toml_names_the_file(tmp_path):
    path = _file(tmp_path, "[[eggs]\nweek = ")
    with pytest.raises(EggFileError, match="not valid TOML") as caught:
        read_spots(path)
    assert str(path) in str(caught.value)


def test_an_egg_with_no_page_names_the_file_the_egg_and_the_field(tmp_path):
    path = _file(tmp_path, GOOD.replace('page = "/a/"\n', ""))
    with pytest.raises(EggFileError, match="no page in egg 1") as caught:
        read_spots(path)
    assert str(path) in str(caught.value)


def test_an_egg_with_a_week_that_is_not_a_number_names_the_file(tmp_path):
    path = _file(tmp_path, GOOD.replace("week = 8", 'week = "eight"'))
    with pytest.raises(EggFileError, match="wrong value in egg 1") as caught:
        read_spots(path)
    assert str(path) in str(caught.value)


def test_a_spot_with_list_conditions_reads_back_the_same(tmp_path):
    path = tmp_path / "2026.toml"
    conditions = {"open": ["game-3"], "trail": ["a", "b"]}
    spot = Spot(week=8, page="/a/", target="t", action="tap2", reason="r", conditions=conditions)
    append_spots(path, [spot])
    assert [each.conditions for each in read_spots(path)] == [conditions]


def test_a_value_of_another_type_is_still_an_error(tmp_path):
    spot = Spot(week=8, page="/a/", target="t", action="tap2", reason="r", conditions={"open": {"a": 1}})
    with pytest.raises(ValueError, match="must be a string"):
        append_spots(tmp_path / "2026.toml", [spot])
