"""
The route table of the front door: each route maps to the model and the effort of the spec, and a route with no
Claude call has no row to read.
"""
import pytest

from facts import writer
from facts.writer import ROUTE_MODELS, RouteModel, route_model


def test_the_table_holds_the_model_and_the_effort_of_each_route_of_the_spec():
    assert ROUTE_MODELS["league_topic"] is None and ROUTE_MODELS["miss"] is None
    assert route_model("personal_topic") == RouteModel("claude-sonnet-5-5", "medium")
    assert route_model("free_answer") == RouteModel("claude-sonnet-5-5", "low")


def test_the_advisor_calls_read_the_rows_of_the_judgment_topics():
    assert (writer.ANALYZER_MODEL, writer.ANALYZER_EFFORT) == route_model("trade_check")
    assert (writer.FINDER_PICK_MODEL, writer.FINDER_PICK_EFFORT) == route_model("trade_ideas")
    assert (writer.SELL_HIGH_MODEL, writer.SELL_HIGH_EFFORT) == route_model("sell_high")


def test_a_route_with_no_claude_call_has_no_row_to_read():
    with pytest.raises(ValueError):
        route_model("miss")
