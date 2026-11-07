"""
Tests for the egg file: a bad file raises EggFileError with the file name and the problem.
Each test writes a real temp file.
"""
import pytest

from eggs.eggfile import EggFileError, read_spots

GOOD = '[[eggs]]\nweek = 8\npage = "/a/"\ntarget = "t"\naction = "tap3"\nconfirmed = true\n'


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
