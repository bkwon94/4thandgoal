Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Base revision: `17f45a15d1c324e36beefd0da29b77fe56b7ef91`.
All source excerpts below come from Git objects at the stated revision.
No behavior test or cold task runs during this static capture.

## `CLAUDE.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–13

```text
1: # 4thandgoal
2: 
3: This repo holds three apps. The site and the pipeline each have a CLAUDE.md with its own commands and rules. Read the one for the app you change.
4: 
5: - [Site](apps/site/README.md) in `apps/site/` is the Next.js site. Its build copies `clients/<slug>/published/` of one client into `public/` and renders each `page.json` and its images.
6: - [Pipeline](apps/pipeline/README.md) in `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `clients/<slug>/published/`.
7: - [API](apps/api/README.md) in `apps/api/` serves the trade analyzer and deploys to Fly. Its product code imports no pipeline code. Run `make help` in it.
8: 
9: For module ownership, follow root instructions → app README → owner README → module and test.
10: Choose the responsibility in the app map, then follow its owner links.
11: 
12: The root holds one uv workspace and one pnpm workspace, each with one lock file: `uv.lock` and `pnpm-lock.yaml`.
13: Run `uv sync --all-packages` and `pnpm install` at the root. A member runs with `uv run --exact --package <name>`.
```

## `apps/api/README.md` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–17

```text
1: # Cornerstone API
2: 
3: The FastAPI app serves each client through domain packages and deploys to Fly.
4: Its product code imports no pipeline code.
5: API tests reuse pipeline fixtures and README-rule helpers; these test dependencies do not define product ownership.
6: 
7: ## Module map
8: 
9: - HTTP composition: the [API owner](src/cornerstone_api/README.md) creates the app and mounts client routes in [app.py](src/cornerstone_api/app.py).
10: - App state and limits: the [API owner](src/cornerstone_api/README.md) owns client state, access checks, and daily answer allowances.
11: - Analyzer routes: the [analyzer owner](../../packages/analyzer/README.md) owns trade grades, caches, and persistent grade limits. The API mounts those routes.
12: 
13: ## Commands
14: 
15: Run `make help` in `apps/api/` for the app commands.
16: Run `make check-fast` for lint, types, and rules.
17: Run `make check` for lint, types, and all tests.
```

## Root diff

```diff
diff --git a/CLAUDE.md b/CLAUDE.md
index 8e9b08d2..e6607a70 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -2,9 +2,12 @@
 
 This repo holds three apps. The site and the pipeline each have a CLAUDE.md with its own commands and rules. Read the one for the app you change.
 
-- `apps/site/` is the Next.js site. Its build copies `clients/<slug>/published/` of one client into `public/` and renders each `page.json` and its images.
-- `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `clients/<slug>/published/`.
-- `apps/api/` is the API of the trade analyzer. It imports the pipeline and deploys to Fly. Run `make help` in it.
+- [Site](apps/site/README.md) in `apps/site/` is the Next.js site. Its build copies `clients/<slug>/published/` of one client into `public/` and renders each `page.json` and its images.
+- [Pipeline](apps/pipeline/README.md) in `apps/pipeline/` is the Python pipeline. It builds each week and publishes it into `clients/<slug>/published/`.
+- [API](apps/api/README.md) in `apps/api/` serves the trade analyzer and deploys to Fly. Its product code imports no pipeline code. Run `make help` in it.
+
+For module ownership, follow root instructions → app README → owner README → module and test.
+Choose the responsibility in the app map, then follow its owner links.
 
 The root holds one uv workspace and one pnpm workspace, each with one lock file: `uv.lock` and `pnpm-lock.yaml`.
 Run `uv sync --all-packages` and `pnpm install` at the root. A member runs with `uv run --exact --package <name>`.
```

## `apps/api/pyproject.toml` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–74

```text
1: # The Cornerstone API app: the FastAPI service of the trade analyzer, a thin uv member apart from the pipeline.
2: # It lists each package it imports, so "uv run --exact --package cpc-api" fails an import it does not list.
3: [project]
4: name = "cpc-api"
5: version = "0.1.0"
6: description = "Serves the Cornerstone trade analyzer over HTTP."
7: authors = [
8:     { name = "Brian Kwon", email = "bkwon94@gmail.com" }
9: ]
10: requires-python = ">=3.11"
11: dependencies = [
12:     "cpc-analyzer",
13:     "cpc-eggs",
14:     "cpc-facts",
15:     "cpc-league",
16:     "cpc-managers",
17:     "fastapi>=0.158.0",
18:     "httpx>=0.28.1",
19:     "pydantic>=2.14.1",
20:     # The exact pin pairs with ai 7.0.159 and @ai-sdk/react 4.0.163 of the site. VercelAIAdapter speaks the stream of
21:     # AI SDK v7 at sdk_version=7, and its docs give no minimum version, so a change of either side moves both pins.
22:     "pydantic-ai-slim[anthropic,ui]==2.66.0",
23:     "uvicorn>=0.54.0",
24: ]
25: 
26: [tool.uv.sources]
27: cornerstone = { workspace = true }
28: cpc-analyzer = { workspace = true }
29: cpc-eggs = { workspace = true }
30: cpc-facts = { workspace = true }
31: cpc-league = { workspace = true }
32: cpc-managers = { workspace = true }
33: 
34: [build-system]
35: requires = ["uv_build>=0.8.18,<0.9.0"]
36: build-backend = "uv_build"
37: 
38: # The tests read the fixtures and the helper modules of the pipeline tests, so only the dev group lists the pipeline.
39: # The image installs no dev group, so it holds no pipeline code.
40: [dependency-groups]
41: dev = [
42:     "cornerstone",
43:     "pyright>=1.1.414",
44:     "pytest>=9.1.1",
45:     "pytest-xdist>=3.8.0",
46:     "ruff==0.17.3",
47: ]
48: 
49: [tool.pytest.ini_options]
50: markers = ["live: calls a real external API"]
51: addopts = "-m 'not live'"
52: 
53: [tool.ruff]
54: line-length = 120
55: 
56: # The API imports the analyzer, the eggs, the league, and the facts packages as its own code, so each sorts as first
57: # party.
58: [tool.ruff.lint.isort]
59: known-first-party = ["analyzer", "cornerstone_api", "eggs", "facts", "league", "managers"]
60: 
61: # Pyright checks only the listed modules in basic mode. Each ticket adds the modules it touches.
62: [tool.pyright]
63: typeCheckingMode = "basic"
64: include = ["src/cornerstone_api/app.py", "src/cornerstone_api/refresh.py", "src/cornerstone_api/ask.py",
65:            "src/cornerstone_api/ask_wording.py", "src/cornerstone_api/miss_log.py",
66:            "src/cornerstone_api/free_answer.py", "src/cornerstone_api/free_tools.py",
67:            "src/cornerstone_api/free_wording.py", "src/cornerstone_api/free_blocks.py",
68:            "src/cornerstone_api/claude_stream.py", "src/cornerstone_api/caps.py", "src/cornerstone_api/personal_topics.py",
69:            "src/cornerstone_api/personal_facts.py", "src/cornerstone_api/personal_wording.py",
70:            "src/cornerstone_api/answer_store.py", "src/cornerstone_api/chat_turns.py",
71:            "src/cornerstone_api/waiver_targets.py", "src/cornerstone_api/sources.py"]
72: 
73: [tool.uv.build-backend]
74: module-name = "cornerstone_api"
```

## `apps/api/tests/test_rule_api.py` at `dad744db4f3b49732adc1586e08c34be2f381f73`; lines 1–49

```text
1: """
2: Runs the rule tests of the pipeline on the API app: the import layers, the suppression comments, and the READMEs.
3: The rules live in the pipeline tests, and each one takes the root it reads. See ADR 0010 and ADR 0014.
4: """
5: from pathlib import Path
6: 
7: import test_layers as layers
8: import test_rule_readmes as readmes
9: import test_rule_suppressions as suppressions
10: from rule_report import report
11: 
12: ROOT = Path(__file__).resolve().parent.parent
13: SRC = ROOT / "src"
14: MARKER = suppressions.MARKER
15: 
16: # The allow list of the API, in the shape of the allow list of the pipeline. The key is the path from the API app.
17: ALLOW: dict[tuple[str, str], str] = {
18:     ("src/cornerstone_api/app.py",
19:      f"except Exception as error:  # {MARKER}: BLE001 - the app keeps running after a failed refresh"):
20:         "the app keeps running after a failed refresh",
21:     ("src/cornerstone_api/sources.py",
22:      f"read_chart: ChartReader = partial(chart_values, read=claude_reader(parse_call))  # {MARKER}: RUF009"):
23:         "one shared partial holds no state that a call changes",
24: }
25: 
26: 
27: def test_the_api_imports_only_from_layer_write_or_a_lower_one():
28:     offenses = layers._import_offenses(layers.SRC, SRC)
29:     assert not offenses, report(offenses)
30: 
31: 
32: def test_the_rule_reads_each_module_of_the_api():
33:     modules = layers._modules(layers.SRC, SRC)
34:     assert {"cornerstone_api.app", "cornerstone_api.sources"} <= set(modules)
35: 
36: 
37: def test_no_comment_in_the_api_silences_a_rule():
38:     offenses = suppressions._comment_offenses(ROOT, ALLOW)
39:     assert not offenses, report(offenses)
40: 
41: 
42: def test_the_allow_list_of_the_api_names_only_lines_that_exist():
43:     found = {(path, text) for path, _, text in suppressions._suppressions(ROOT)}
44:     assert [key for key in ALLOW if key not in found] == []
45: 
46: 
47: def test_each_package_folder_of_the_api_has_a_readme_with_the_three_headings():
48:     offenses = readmes._missing_offenses(ROOT) + readmes._heading_offenses(ROOT) + readmes._length_offenses(ROOT)
49:     assert not offenses, report(offenses)
```

## Complete static API product import inventory

Python AST import statements from all tracked apps/api/src/**/*.py files follow.
This static inventory does not execute imports. No statement imports cornerstone or pipeline.
Test helpers belong to apps/api/tests; pyproject lists cornerstone only in the dev dependency group.
The uv source map declares resolution; it does not add a product dependency.

```text
apps/api/src/cornerstone_api/answer_store.py:5: import json
apps/api/src/cornerstone_api/answer_store.py:6: import sqlite3
apps/api/src/cornerstone_api/answer_store.py:7: from collections.abc import Iterator
apps/api/src/cornerstone_api/answer_store.py:8: from contextlib import contextmanager
apps/api/src/cornerstone_api/answer_store.py:9: from datetime import datetime
apps/api/src/cornerstone_api/answer_store.py:10: from pathlib import Path
apps/api/src/cornerstone_api/app.py:13: import functools
apps/api/src/cornerstone_api/app.py:14: import hmac
apps/api/src/cornerstone_api/app.py:15: import logging
apps/api/src/cornerstone_api/app.py:16: import sys
apps/api/src/cornerstone_api/app.py:17: import threading
apps/api/src/cornerstone_api/app.py:18: from collections.abc import Callable, Mapping, Sequence
apps/api/src/cornerstone_api/app.py:19: from datetime import datetime
apps/api/src/cornerstone_api/app.py:20: from pathlib import Path
apps/api/src/cornerstone_api/app.py:22: from fastapi import Depends, FastAPI, Request, Response
apps/api/src/cornerstone_api/app.py:23: from fastapi.middleware.cors import CORSMiddleware
apps/api/src/cornerstone_api/app.py:24: from fastapi.responses import JSONResponse
apps/api/src/cornerstone_api/app.py:26: from analyzer import routes as analyzer_routes
apps/api/src/cornerstone_api/app.py:27: from analyzer.advisor import read_trade
apps/api/src/cornerstone_api/app.py:28: from analyzer.cache import ResultCache, TeamsCache
apps/api/src/cornerstone_api/app.py:29: from analyzer.finder_pick import pick_trades
apps/api/src/cornerstone_api/app.py:30: from analyzer.finder_search import search as search_trades
apps/api/src/cornerstone_api/app.py:31: from analyzer.ratelimit import GradeLimiter, RateLimiter, request_address
apps/api/src/cornerstone_api/app.py:32: from analyzer.sell_high import pick_sells
apps/api/src/cornerstone_api/app.py:33: from analyzer.trade_news import NEWS
apps/api/src/cornerstone_api/app.py:34: from analyzer.tunables import GRADES_PER_DAY, GRADES_PER_MINUTE
apps/api/src/cornerstone_api/app.py:35: from cornerstone_api import ask as ask_routes
apps/api/src/cornerstone_api/app.py:36: from cornerstone_api import free_answer as free_routes
apps/api/src/cornerstone_api/app.py:37: from cornerstone_api import personal_topics, suggestions, trade_topics
apps/api/src/cornerstone_api/app.py:38: from cornerstone_api import refresh as refresh_routes
apps/api/src/cornerstone_api/app.py:39: from cornerstone_api.answer_store import AnswerStore
apps/api/src/cornerstone_api/app.py:40: from cornerstone_api.caps import Caps
apps/api/src/cornerstone_api/app.py:41: from cornerstone_api.miss_log import MissLog
apps/api/src/cornerstone_api/app.py:42: from cornerstone_api.personal_topics import LIVE_CACHE_SECONDS, LiveCache
apps/api/src/cornerstone_api/app.py:43: from cornerstone_api.settings import Settings, ask_dir, commissioner_key_env, eggs_dir, passphrase_env, repo_from_env
apps/api/src/cornerstone_api/app.py:44: from cornerstone_api.sources import Sources
apps/api/src/cornerstone_api/app.py:45: from cornerstone_api.value_models import VALUE_MODELS
apps/api/src/cornerstone_api/app.py:46: from eggs import routes as eggs_routes
apps/api/src/cornerstone_api/app.py:47: from eggs.store import EggStore
apps/api/src/cornerstone_api/app.py:48: from eggs.tunables import BOARD_READS_PER_MINUTE, BOARD_WINDOW_SECONDS, CHECK_WINDOW_SECONDS, CHECKS_PER_HOUR
apps/api/src/cornerstone_api/app.py:49: from eggs.values import EggsValues
apps/api/src/cornerstone_api/app.py:50: from league.client import Client, SettingsFetch, load_client
apps/api/src/cornerstone_api/app.py:51: from league.jev import JEV
apps/api/src/cornerstone_api/app.py:52: from league.jev_port import Jev
apps/api/src/cornerstone_api/app.py:53: from league.nflverse import http_get
apps/api/src/cornerstone_api/app.py:54: from league.paths import provider_cache_dir
apps/api/src/cornerstone_api/app.py:55: from league.provider.sleeper import SleeperProvider, fetch_settings
apps/api/src/cornerstone_api/app.py:56: from league.tunables import TEAMS_CACHE_SECONDS
apps/api/src/cornerstone_api/ask.py:5: import logging
apps/api/src/cornerstone_api/ask.py:6: import threading
apps/api/src/cornerstone_api/ask.py:7: import time
apps/api/src/cornerstone_api/ask.py:8: from collections.abc import Callable
apps/api/src/cornerstone_api/ask.py:9: from dataclasses import dataclass, field
apps/api/src/cornerstone_api/ask.py:10: from datetime import datetime
apps/api/src/cornerstone_api/ask.py:11: from typing import Annotated, Literal
apps/api/src/cornerstone_api/ask.py:13: from fastapi import APIRouter, Depends, HTTPException, Request
apps/api/src/cornerstone_api/ask.py:14: from pydantic import BaseModel, Field
apps/api/src/cornerstone_api/ask.py:16: from cornerstone_api.ask_wording import (
    ABOUT_LEAGUE,
    ABUSE,
    DATA_CAN_ANSWER,
    FITS_TOPIC,
    NAMES_TEAM,
    TEAM,
    TOPIC,
    route_questions,
    route_state,
    team_key,
)
apps/api/src/cornerstone_api/ask.py:28: from cornerstone_api.caps import Caps
apps/api/src/cornerstone_api/ask.py:29: from cornerstone_api.chat_turns import Turn, Turns, with_turns
apps/api/src/cornerstone_api/ask.py:30: from cornerstone_api.miss_log import MissLog
apps/api/src/cornerstone_api/ask.py:31: from league.jev_port import Jev, JevError, JevResponse
apps/api/src/cornerstone_api/ask_wording.py:5: import re
apps/api/src/cornerstone_api/ask_wording.py:7: from league.jev_port import ChoiceQuestion, NoulQuestion
apps/api/src/cornerstone_api/caps.py:5: import logging
apps/api/src/cornerstone_api/caps.py:6: import sqlite3
apps/api/src/cornerstone_api/caps.py:7: import threading
apps/api/src/cornerstone_api/caps.py:8: from collections.abc import Iterator
apps/api/src/cornerstone_api/caps.py:9: from contextlib import contextmanager
apps/api/src/cornerstone_api/caps.py:10: from dataclasses import dataclass
apps/api/src/cornerstone_api/caps.py:11: from datetime import date, datetime
apps/api/src/cornerstone_api/caps.py:12: from pathlib import Path
apps/api/src/cornerstone_api/caps.py:13: from typing import Literal
apps/api/src/cornerstone_api/caps.py:15: from pydantic_ai.usage import RunUsage
apps/api/src/cornerstone_api/chat_turns.py:5: from typing import Annotated, Any
apps/api/src/cornerstone_api/chat_turns.py:7: from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field
apps/api/src/cornerstone_api/chat_turns.py:8: from pydantic_ai.messages import CachePoint, ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
apps/api/src/cornerstone_api/claude_stream.py:5: import logging
apps/api/src/cornerstone_api/claude_stream.py:6: from collections.abc import AsyncIterator, Callable
apps/api/src/cornerstone_api/claude_stream.py:7: from dataclasses import dataclass, field
apps/api/src/cornerstone_api/claude_stream.py:8: from typing import Any
apps/api/src/cornerstone_api/claude_stream.py:10: import anyio
apps/api/src/cornerstone_api/claude_stream.py:11: from pydantic_ai import Agent
apps/api/src/cornerstone_api/claude_stream.py:12: from pydantic_ai.agent import AgentRunResult
apps/api/src/cornerstone_api/claude_stream.py:13: from pydantic_ai.messages import ModelMessage
apps/api/src/cornerstone_api/claude_stream.py:14: from pydantic_ai.models import Model
apps/api/src/cornerstone_api/claude_stream.py:15: from pydantic_ai.ui.vercel_ai import VercelAIAdapter
apps/api/src/cornerstone_api/claude_stream.py:16: from pydantic_ai.ui.vercel_ai.request_types import SubmitMessage, TextUIPart, UIMessage
apps/api/src/cornerstone_api/claude_stream.py:17: from pydantic_ai.ui.vercel_ai.response_types import (
    BaseChunk,
    DataChunk,
    DoneChunk,
    ErrorChunk,
    FinishChunk,
    MessageMetadataChunk,
    StartChunk,
    TextDeltaChunk,
    TextEndChunk,
    TextStartChunk,
)
apps/api/src/cornerstone_api/claude_stream.py:30: from cornerstone_api.ask import YES, Asker
apps/api/src/cornerstone_api/claude_stream.py:31: from cornerstone_api.caps import sonnet_cost
apps/api/src/cornerstone_api/claude_stream.py:32: from cornerstone_api.free_wording import check_questions, check_state, sentence_key, sentences
apps/api/src/cornerstone_api/claude_stream.py:33: from league.jev_port import Jev, JevError
apps/api/src/cornerstone_api/free_answer.py:5: import hashlib
apps/api/src/cornerstone_api/free_answer.py:6: import json
apps/api/src/cornerstone_api/free_answer.py:7: import logging
apps/api/src/cornerstone_api/free_answer.py:8: import threading
apps/api/src/cornerstone_api/free_answer.py:9: from collections.abc import AsyncIterator, Callable
apps/api/src/cornerstone_api/free_answer.py:10: from dataclasses import dataclass, field
apps/api/src/cornerstone_api/free_answer.py:11: from datetime import datetime
apps/api/src/cornerstone_api/free_answer.py:12: from typing import Any
apps/api/src/cornerstone_api/free_answer.py:14: import anyio
apps/api/src/cornerstone_api/free_answer.py:15: from fastapi import APIRouter, HTTPException, Request
apps/api/src/cornerstone_api/free_answer.py:16: from fastapi.responses import StreamingResponse
apps/api/src/cornerstone_api/free_answer.py:17: from pydantic import BaseModel, ConfigDict, Field
apps/api/src/cornerstone_api/free_answer.py:18: from pydantic_ai import Agent, RunContext
apps/api/src/cornerstone_api/free_answer.py:19: from pydantic_ai.capabilities import Caching
apps/api/src/cornerstone_api/free_answer.py:20: from pydantic_ai.models import Model
apps/api/src/cornerstone_api/free_answer.py:21: from pydantic_ai.models.anthropic import AnthropicModelSettings
apps/api/src/cornerstone_api/free_answer.py:22: from pydantic_ai.ui.vercel_ai.response_types import BaseChunk, DoneChunk, FinishChunk, StartChunk
apps/api/src/cornerstone_api/free_answer.py:24: from analyzer.routes import ServedClient
apps/api/src/cornerstone_api/free_answer.py:25: from cornerstone_api import free_tools
apps/api/src/cornerstone_api/free_answer.py:26: from cornerstone_api.answer_store import AnswerStore
apps/api/src/cornerstone_api/free_answer.py:27: from cornerstone_api.ask import QUESTION_MAX, WEEK_MAX, Asker, ClientAsker, Route
apps/api/src/cornerstone_api/free_answer.py:28: from cornerstone_api.chat_turns import Turn, Turns, turn_messages, turns_instructions
apps/api/src/cornerstone_api/free_answer.py:29: from cornerstone_api.claude_stream import Checker, Outcome, Writer, adapter, checked_answer, data, kept_text
apps/api/src/cornerstone_api/free_answer.py:30: from cornerstone_api.free_blocks import BLOCK, Block, row_sentences
apps/api/src/cornerstone_api/free_answer.py:31: from cornerstone_api.free_wording import INSTRUCTIONS, rewrite_prompt, run_instructions
apps/api/src/cornerstone_api/free_answer.py:32: from cornerstone_api.personal_facts import _ahead
apps/api/src/cornerstone_api/free_answer.py:33: from cornerstone_api.personal_topics import LiveCache, _load
apps/api/src/cornerstone_api/free_answer.py:34: from facts.writer import route_model
apps/api/src/cornerstone_api/free_answer.py:35: from league.live import fetch_live_week
apps/api/src/cornerstone_api/free_answer.py:36: from league.paths import history_root
apps/api/src/cornerstone_api/free_answer.py:37: from league.season_inputs import SeasonInputs
apps/api/src/cornerstone_api/free_answer.py:38: from managers.grade import roster_places
apps/api/src/cornerstone_api/free_blocks.py:5: from typing import Annotated, Literal
apps/api/src/cornerstone_api/free_blocks.py:7: from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator
apps/api/src/cornerstone_api/free_tools.py:5: import re
apps/api/src/cornerstone_api/free_tools.py:6: from collections import defaultdict
apps/api/src/cornerstone_api/free_tools.py:7: from collections.abc import Callable
apps/api/src/cornerstone_api/free_tools.py:8: from dataclasses import dataclass, field
apps/api/src/cornerstone_api/free_tools.py:9: from decimal import Decimal
apps/api/src/cornerstone_api/free_tools.py:10: from functools import cached_property
apps/api/src/cornerstone_api/free_tools.py:11: from pathlib import Path
apps/api/src/cornerstone_api/free_tools.py:13: from cornerstone_api.personal_facts import PART_NAMES
apps/api/src/cornerstone_api/free_tools.py:14: from league.history import load_saved_weeks
apps/api/src/cornerstone_api/free_tools.py:15: from league.models import History, PastWeek
apps/api/src/cornerstone_api/free_tools.py:16: from league.numbers import r2
apps/api/src/cornerstone_api/free_tools.py:17: from league.parse import player_name
apps/api/src/cornerstone_api/free_tools.py:18: from league.provider.raw import RawWeek
apps/api/src/cornerstone_api/free_tools.py:19: from league.ranks import OUT_STATUSES, STATUS_WORDS
apps/api/src/cornerstone_api/free_tools.py:20: from league.standings_table import season_records, standings_order, week_median
apps/api/src/cornerstone_api/free_tools.py:21: from managers.grade import ManagerGrade
apps/api/src/cornerstone_api/free_wording.py:5: import re
apps/api/src/cornerstone_api/free_wording.py:7: from cornerstone_api.free_blocks import BLOCK_MEANING
apps/api/src/cornerstone_api/free_wording.py:8: from league.jev_port import NoulQuestion
apps/api/src/cornerstone_api/miss_log.py:5: import json
apps/api/src/cornerstone_api/miss_log.py:6: import sqlite3
apps/api/src/cornerstone_api/miss_log.py:7: from collections.abc import Iterator
apps/api/src/cornerstone_api/miss_log.py:8: from contextlib import contextmanager
apps/api/src/cornerstone_api/miss_log.py:9: from dataclasses import dataclass
apps/api/src/cornerstone_api/miss_log.py:10: from datetime import datetime, timedelta
apps/api/src/cornerstone_api/miss_log.py:11: from pathlib import Path
apps/api/src/cornerstone_api/personal_facts.py:5: from dataclasses import dataclass
apps/api/src/cornerstone_api/personal_facts.py:6: from typing import Literal
apps/api/src/cornerstone_api/personal_facts.py:8: from analyzer.trade_jev import weak_slot_rows, weak_starting_slots
apps/api/src/cornerstone_api/personal_facts.py:9: from cornerstone_api.waiver_targets import waiver_facts
apps/api/src/cornerstone_api/personal_facts.py:10: from league.lineup import cannot_play_now, lineup_now
apps/api/src/cornerstone_api/personal_facts.py:11: from league.numbers import ordinal
apps/api/src/cornerstone_api/personal_facts.py:12: from league.provider.raw import RawTrending
apps/api/src/cornerstone_api/personal_facts.py:13: from league.season_inputs import SeasonInputs
apps/api/src/cornerstone_api/personal_facts.py:14: from league.snapshot import Snapshot
apps/api/src/cornerstone_api/personal_facts.py:15: from managers.grade import ManagerGrade, Starter, roster_grades, roster_starters
apps/api/src/cornerstone_api/personal_topics.py:6: import hashlib
apps/api/src/cornerstone_api/personal_topics.py:7: import json
apps/api/src/cornerstone_api/personal_topics.py:8: import logging
apps/api/src/cornerstone_api/personal_topics.py:9: import threading
apps/api/src/cornerstone_api/personal_topics.py:10: import time
apps/api/src/cornerstone_api/personal_topics.py:11: from collections.abc import AsyncIterator, Awaitable, Callable
apps/api/src/cornerstone_api/personal_topics.py:12: from dataclasses import dataclass
apps/api/src/cornerstone_api/personal_topics.py:13: from typing import Any
apps/api/src/cornerstone_api/personal_topics.py:15: import anyio
apps/api/src/cornerstone_api/personal_topics.py:16: from fastapi import APIRouter, HTTPException, Request
apps/api/src/cornerstone_api/personal_topics.py:17: from fastapi.responses import StreamingResponse
apps/api/src/cornerstone_api/personal_topics.py:18: from pydantic import BaseModel, ConfigDict, Field
apps/api/src/cornerstone_api/personal_topics.py:19: from pydantic_ai import Agent
apps/api/src/cornerstone_api/personal_topics.py:20: from pydantic_ai.capabilities import Caching
apps/api/src/cornerstone_api/personal_topics.py:21: from pydantic_ai.models import Model
apps/api/src/cornerstone_api/personal_topics.py:22: from pydantic_ai.models.anthropic import AnthropicModelSettings
apps/api/src/cornerstone_api/personal_topics.py:23: from pydantic_ai.ui.vercel_ai.response_types import (
    BaseChunk,
    DoneChunk,
    ErrorChunk,
    FinishChunk,
    StartChunk,
)
apps/api/src/cornerstone_api/personal_topics.py:31: from analyzer.routes import ServedClient
apps/api/src/cornerstone_api/personal_topics.py:32: from cornerstone_api.answer_store import AnswerStore
apps/api/src/cornerstone_api/personal_topics.py:33: from cornerstone_api.ask import QUESTION_MAX, Asker, ClientAsker
apps/api/src/cornerstone_api/personal_topics.py:34: from cornerstone_api.caps import CapHit
apps/api/src/cornerstone_api/personal_topics.py:35: from cornerstone_api.chat_turns import Turn, Turns, turn_messages, turns_instructions
apps/api/src/cornerstone_api/personal_topics.py:36: from cornerstone_api.claude_stream import (
    STREAM_ERROR,
    Checker,
    Outcome,
    Writer,
    adapter,
    checked_answer,
    data,
    kept_text,
)
apps/api/src/cornerstone_api/personal_topics.py:46: from cornerstone_api.personal_facts import (
    PersonalFacts,
    PersonalTopic,
    judged_waiver,
    live_grades,
    topic_facts,
)
apps/api/src/cornerstone_api/personal_topics.py:53: from cornerstone_api.personal_wording import (
    FACT_MEANINGS,
    INSTRUCTIONS,
    TOPIC_ASKS,
    WAIVER_ADD,
    WAIVER_STASH,
    check_question,
    rewrite_prompt,
    topic_prompt,
)
apps/api/src/cornerstone_api/personal_topics.py:63: from cornerstone_api.waiver_targets import judge
apps/api/src/cornerstone_api/personal_topics.py:64: from facts.writer import route_model
apps/api/src/cornerstone_api/personal_topics.py:65: from league.jev_port import Jev, JevError
apps/api/src/cornerstone_api/personal_topics.py:66: from league.provider.raw import RawTrending
apps/api/src/cornerstone_api/personal_topics.py:67: from league.snapshot import Snapshot
apps/api/src/cornerstone_api/personal_topics.py:68: from managers.grade import ManagerGrade, Starter
apps/api/src/cornerstone_api/personal_wording.py:5: import json
apps/api/src/cornerstone_api/personal_wording.py:7: from league.jev_port import NoulQuestion
apps/api/src/cornerstone_api/refresh.py:5: from fastapi import APIRouter, Request
apps/api/src/cornerstone_api/refresh.py:7: from analyzer.errors import season_in_progress
apps/api/src/cornerstone_api/refresh.py:8: from analyzer.routes import ServedClient
apps/api/src/cornerstone_api/settings.py:6: import os
apps/api/src/cornerstone_api/settings.py:7: from collections.abc import Iterable, Mapping
apps/api/src/cornerstone_api/settings.py:8: from dataclasses import dataclass, field
apps/api/src/cornerstone_api/settings.py:9: from pathlib import Path
apps/api/src/cornerstone_api/settings.py:11: from eggs.keys import commissioner_key_env
apps/api/src/cornerstone_api/settings.py:12: from league.paths import results_cache_dir
apps/api/src/cornerstone_api/sources.py:5: from collections.abc import Callable
apps/api/src/cornerstone_api/sources.py:6: from dataclasses import dataclass
apps/api/src/cornerstone_api/sources.py:7: from datetime import datetime
apps/api/src/cornerstone_api/sources.py:8: from functools import partial
apps/api/src/cornerstone_api/sources.py:10: from facts.writer import parse_call
apps/api/src/cornerstone_api/sources.py:11: from league.chart import chart_values, claude_reader
apps/api/src/cornerstone_api/sources.py:12: from league.client import Client
apps/api/src/cornerstone_api/sources.py:13: from league.history import PastLegFetcher
apps/api/src/cornerstone_api/sources.py:14: from league.live import (
    ChartReader,
    RefreshResult,
    SleeperFetcher,
    fetch_current_week,
    fetch_live_week,
    live_rosters_snapshot,
    live_snapshot,
    refresh_sources,
)
apps/api/src/cornerstone_api/sources.py:24: from league.models import Week
apps/api/src/cornerstone_api/sources.py:25: from league.nflverse import CACHE_MAX_AGE_SECONDS, http_get
apps/api/src/cornerstone_api/sources.py:26: from league.provider.raw import RawTrending
apps/api/src/cornerstone_api/sources.py:27: from league.provider.sleeper import fetch_past_week, fetch_trending
apps/api/src/cornerstone_api/sources.py:28: from league.snapshot import Snapshot
apps/api/src/cornerstone_api/suggestion_wording.py:6: from cornerstone_api.ask_wording import TOPICS
apps/api/src/cornerstone_api/suggestion_wording.py:7: from league.jev_port import ChoiceQuestion, NoulQuestion
apps/api/src/cornerstone_api/suggestions.py:5: import json
apps/api/src/cornerstone_api/suggestions.py:6: import logging
apps/api/src/cornerstone_api/suggestions.py:7: from typing import cast, get_args
apps/api/src/cornerstone_api/suggestions.py:9: import anyio
apps/api/src/cornerstone_api/suggestions.py:10: from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
apps/api/src/cornerstone_api/suggestions.py:11: from pydantic import BaseModel, ConfigDict, Field
apps/api/src/cornerstone_api/suggestions.py:12: from pydantic_ai.models import Model
apps/api/src/cornerstone_api/suggestions.py:14: from analyzer.routes import ServedClient
apps/api/src/cornerstone_api/suggestions.py:15: from analyzer.sell_facts import sell_sheet, sheet_players
apps/api/src/cornerstone_api/suggestions.py:16: from cornerstone_api.answer_store import AnswerStore
apps/api/src/cornerstone_api/suggestions.py:17: from cornerstone_api.ask import YES, Asker, ClientAsker
apps/api/src/cornerstone_api/suggestions.py:18: from cornerstone_api.ask_wording import TOPICS
apps/api/src/cornerstone_api/suggestions.py:19: from cornerstone_api.personal_facts import PersonalTopic, trade_ideas_fact
apps/api/src/cornerstone_api/suggestions.py:20: from cornerstone_api.personal_topics import Live, claude_answer, load_live, shown_facts
apps/api/src/cornerstone_api/suggestions.py:21: from cornerstone_api.suggestion_wording import (
    SELL_CHOICE,
    SELL_NOUL,
    lift_key,
    lift_questions,
    lift_state,
    sell_questions,
    sell_state,
)
apps/api/src/cornerstone_api/suggestions.py:30: from cornerstone_api.trade_topics import TradeTopic, trade_key
apps/api/src/cornerstone_api/suggestions.py:31: from cornerstone_api.trade_wording import option_keys
apps/api/src/cornerstone_api/suggestions.py:32: from league.jev_port import Jev, JevError
apps/api/src/cornerstone_api/suggestions.py:33: from league.paths import week_label
apps/api/src/cornerstone_api/suggestions.py:34: from league.ranks import recent_points_per_game, season_points_per_game
apps/api/src/cornerstone_api/suggestions.py:35: from league.tunables import LINEUP_WEEKS
apps/api/src/cornerstone_api/trade_topics.py:5: import contextvars
apps/api/src/cornerstone_api/trade_topics.py:6: import hashlib
apps/api/src/cornerstone_api/trade_topics.py:7: import json
apps/api/src/cornerstone_api/trade_topics.py:8: import logging
apps/api/src/cornerstone_api/trade_topics.py:9: import queue
apps/api/src/cornerstone_api/trade_topics.py:10: import threading
apps/api/src/cornerstone_api/trade_topics.py:11: from collections.abc import Callable, Iterator
apps/api/src/cornerstone_api/trade_topics.py:12: from dataclasses import asdict, dataclass
apps/api/src/cornerstone_api/trade_topics.py:13: from typing import Literal
apps/api/src/cornerstone_api/trade_topics.py:15: from fastapi import APIRouter, HTTPException, Request
apps/api/src/cornerstone_api/trade_topics.py:16: from fastapi.responses import StreamingResponse
apps/api/src/cornerstone_api/trade_topics.py:17: from pydantic import BaseModel, Field
apps/api/src/cornerstone_api/trade_topics.py:19: from analyzer import routes as analyzer_routes
apps/api/src/cornerstone_api/trade_topics.py:20: from analyzer.finder_search import Anchor, Limit
apps/api/src/cornerstone_api/trade_topics.py:21: from analyzer.routes import FindRequest, ServedClient
apps/api/src/cornerstone_api/trade_topics.py:22: from analyzer.stage import Stage
apps/api/src/cornerstone_api/trade_topics.py:23: from analyzer.trade import GivenPlayer, ProposedTrade, TradeSide
apps/api/src/cornerstone_api/trade_topics.py:24: from cornerstone_api.ask import QUESTION_MAX, YES, Asker, ClientAsker
apps/api/src/cornerstone_api/trade_topics.py:25: from cornerstone_api.chat_turns import Turn, Turns, with_turns
apps/api/src/cornerstone_api/trade_topics.py:26: from cornerstone_api.trade_wording import (
    AIM_POSITION,
    AIMS_POSITION,
    CONTEXT,
    GETS_NAMED,
    GETS_PLAYER,
    GIVES_NAMED,
    GIVES_PLAYER,
    IDEAS_CONTEXT,
    KEEPS_NAMED,
    KEEPS_POSITION,
    KEPT_PLAYER,
    limit_questions,
    option_keys,
    pick_questions,
    pick_state,
    player_line,
)
apps/api/src/cornerstone_api/trade_topics.py:44: from facts.writer import metered_press
apps/api/src/cornerstone_api/trade_topics.py:45: from league.jev_port import Jev, JevError, JevResponse
apps/api/src/cornerstone_api/trade_wording.py:5: import re
apps/api/src/cornerstone_api/trade_wording.py:7: from league.jev_port import ChoiceQuestion, NoulQuestion
apps/api/src/cornerstone_api/value_models.py:5: from analyzer.values import AnalyzerValues
apps/api/src/cornerstone_api/value_models.py:6: from eggs.values import EggsValues
apps/api/src/cornerstone_api/value_models.py:7: from league.client import ValueModels
apps/api/src/cornerstone_api/value_models.py:8: from league.values import LeagueValues
apps/api/src/cornerstone_api/waiver_targets.py:5: import logging
apps/api/src/cornerstone_api/waiver_targets.py:6: from dataclasses import dataclass
apps/api/src/cornerstone_api/waiver_targets.py:8: from analyzer.jev_waves import JevWaves, WaveRequest
apps/api/src/cornerstone_api/waiver_targets.py:9: from analyzer.trade_jev import TRADE_POSITIONS, YES_AT, weak_starting_slots
apps/api/src/cornerstone_api/waiver_targets.py:10: from cornerstone_api.personal_wording import waiver_questions
apps/api/src/cornerstone_api/waiver_targets.py:11: from league.history import player_points
apps/api/src/cornerstone_api/waiver_targets.py:12: from league.jev_port import Jev, JevError
apps/api/src/cornerstone_api/waiver_targets.py:13: from league.lineup import allowed_positions, lineup_now
apps/api/src/cornerstone_api/waiver_targets.py:14: from league.projection import next_week, rest_of_season
apps/api/src/cornerstone_api/waiver_targets.py:15: from league.provider.raw import RawTrending
apps/api/src/cornerstone_api/waiver_targets.py:16: from league.ranks import OUT_STATUSES, STATUS_WORDS
apps/api/src/cornerstone_api/waiver_targets.py:17: from league.snapshot import Snapshot, SnapshotPlayer
```
