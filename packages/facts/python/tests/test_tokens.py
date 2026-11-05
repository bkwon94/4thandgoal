"""
Tests for the fact tokens: the page form of a number, the numbers that Nums records, and the number tokens.
The verifier matches each sentence number to these records, so a missed number fails a true sentence.
"""
from facts.tokens import NUMBER_TOKEN, Nums, fact, fmt


def test_fmt_writes_the_shortest_two_decimal_form():
    assert [fmt(106.8), fmt(21.0), fmt(8.125), fmt(-3.456)] == ["106.8", "21", "8.13", "-3.46"]


def test_a_fact_carries_every_number_as_the_page_shows_it():
    n = Nums()
    text = f"Team A scored {n(118.40)} to go {n.record(5, 2)}, {n.ord(3)} in the league."
    built = fact("ST.1", text, n, teams=["Team A"], players=[])
    assert built.text == "Team A scored 118.4 to go 5-2, 3rd in the league."
    assert built.numbers == ["118.4", "5", "2", "5-2", "3"]


def test_nums_text_rewrites_decimals_and_records_the_parts_of_a_record():
    n = Nums()
    assert n.text("won 33-30 with 12.50 points, a -4 swing") == "won 33-30 with 12.5 points, a -4 swing"
    assert n.seen == ["33-30", "33", "30", "12.5", "-4", "4"]


def test_the_number_token_keeps_a_record_and_a_negative_number_whole():
    assert NUMBER_TOKEN.findall("a 9-7 record, a -2.5 gap, and 87 points") == ["9-7", "-2.5", "87"]
