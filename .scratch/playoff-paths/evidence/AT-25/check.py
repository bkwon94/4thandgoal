"""
AT-25 evidence test: the Suggestions route of the API on the recorded sources of the suite, run as week 14 and week 15.
It prints the request, the response, and the rank of the race Topic for Bo Girds. Copy it to apps/api/tests to run it.
"""
import json

from fakes import FakeJev
from test_personal_topics import Writer, _api
from test_suggestions import BO_GIRDS, SUGGESTIONS, TUESDAY, Lifts, _publish_topics, _sources_at_week
from test_api import HEADERS

repo = __import__("test_api").repo
settings = __import__("test_api").settings
sources = __import__("test_api").sources


def test_at_25_the_race_topic_rank_in_week_14_and_week_15(settings, sources):
    _publish_topics(settings)
    for week in (14, 15):
        api = _api(settings, _sources_at_week(sources, week), FakeJev(answer=Lifts().answer), Writer())
        body = {"roster_id": BO_GIRDS, "order": TUESDAY, "opened": {}}
        response = api.post(SUGGESTIONS, json=body, headers=HEADERS)
        r = response.json()
        print(f"== the league runs as week {week}")
        print(f"request: POST {SUGGESTIONS} {json.dumps(body)}")
        print(f"response: {response.status_code} picks {r['picks']} urgent {r['urgent']} head_start {r['head_start']}")
        print(f"response facts keys: {sorted(r['facts'])}")
        ranked = [k for k in TUESDAY if k in r["facts"]]
        print(f"rank of playoff_race in the order of the day: {TUESDAY.index('playoff_race') + 1}; "
              f"rank among the Topics with a fact: {ranked.index('playoff_race') + 1}; "
              f"place in the picks: {r['picks'].index('playoff_race') + 1 if 'playoff_race' in r['picks'] else 'not in the 3 picks'}")
