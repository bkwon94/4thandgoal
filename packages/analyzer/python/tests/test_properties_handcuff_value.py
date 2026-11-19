"""
Property test of the trade value of a handcuff: a handcuff in a trade has a value of 0, whatever the chart lists.
Hypothesis draws the chart, the handcuffs, and the players out for the season.
"""
from datetime import date

from hypothesis import given
from hypothesis import strategies as st

from analyzer.trade import _trade_values
from league.models import ChartValues
from league.snapshot import Snapshot

ids = st.text(alphabet="abcdefgh0123456789", min_size=1, max_size=3)


@given(st.dictionaries(ids, st.floats(min_value=0.0, max_value=100.0), max_size=20),
       st.lists(ids, max_size=10), st.sets(ids, max_size=5))
def test_a_handcuff_in_a_trade_has_a_trade_value_of_0(chart, handcuffs, out_for_season):
    # The value read needs only the chart and the players out for the season, so the other fields stay unset.
    snapshot = Snapshot.model_construct(chart=ChartValues(week=1, date=date(2026, 9, 1), values=chart),
                                        out_for_season=out_for_season)
    values = _trade_values(snapshot, handcuffs)
    assert all(values[pid] == 0.0 for pid in handcuffs)
