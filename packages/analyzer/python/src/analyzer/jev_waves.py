"""
The Jev requests of one press, sent in waves under the TypeSafe rate limits of requests and tokens per second.
Each wave runs its requests at once, and the next wave waits until one second after the start of the last.
"""
import json
import logging
import math
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from league.jev_port import Jev, JevError, JevResponse, NoulQuestion

log = logging.getLogger(__name__)

# The limits of the TypeSafe account, from its dashboard: 80 requests per second and 100,000 tokens per second.
REQUESTS_PER_SECOND = 80
TOKENS_PER_SECOND = 100_000
# A token is about 4 characters of the JSON. The count uses 3, so a wave keeps some headroom.
CHARS_PER_TOKEN = 3
WAVE_SECONDS = 1.0


@dataclass(frozen=True)
class WaveRequest:
    """One Jev request of a wave: its state and its questions by key."""
    state: dict
    questions: dict[str, NoulQuestion]


def estimated_tokens(request: WaveRequest) -> int:
    """A high guess of the input tokens of the request: the state and the text of each question."""
    texts = [json.dumps(request.state)] + [
        json.dumps(q.instructions) + q.yes + q.no for q in request.questions.values()]
    return math.ceil(sum(len(text) for text in texts) / CHARS_PER_TOKEN)


def plan_waves(requests: dict[str, WaveRequest]) -> list[list[str]]:
    """The keys of the requests in waves, in order. Each wave stays under both limits of one second."""
    waves: list[list[str]] = []
    wave: list[str] = []
    tokens = 0
    for key, request in requests.items():
        cost = estimated_tokens(request)
        if wave and (len(wave) >= REQUESTS_PER_SECOND or tokens + cost > TOKENS_PER_SECOND):
            waves.append(wave)
            wave, tokens = [], 0
        wave.append(key)
        tokens += cost
    if wave:
        waves.append(wave)
    return waves


class JevWaves:
    """The pacer of the Jev requests of one press. It keeps the start time of its last wave across calls of `ask`.

    So the partner filter, the targets, and the shortlist share one budget per second, as TypeSafe counts it.
    """

    def __init__(self, jev: Jev, clock: Callable[[], float] = time.monotonic,
                 sleep: Callable[[float], None] = time.sleep):
        self.jev = jev
        self.clock = clock
        self.sleep = sleep
        self._last_start: float | None = None
        self.waves_sent = 0

    def ask(self, requests: dict[str, WaveRequest], label: str) -> dict[str, JevResponse | None]:
        """The answer of each request by key. A failed request gives None, and it logs, so one failure never stops
        the press. A caller never reads None as a no.
        """
        answers: dict[str, JevResponse | None] = {}
        for keys in plan_waves(requests):
            if self._last_start is not None:
                wait = self._last_start + WAVE_SECONDS - self.clock()
                if wait > 0:
                    self.sleep(wait)
            self._last_start = self.clock()
            self.waves_sent += 1
            tokens = sum(estimated_tokens(requests[key]) for key in keys)
            log.info("Jev wave %d (%s): %d requests, about %d tokens", self.waves_sent, label, len(keys), tokens)
            with ThreadPoolExecutor(max_workers=len(keys)) as pool:
                futures = {key: pool.submit(self._one, requests[key]) for key in keys}
            for key, future in futures.items():
                result = future.result()
                if isinstance(result, JevError):
                    log.warning("The Jev request %s (%s) failed: %s", key, label, result)
                    answers[key] = None
                else:
                    answers[key] = result
        return answers

    def _one(self, request: WaveRequest) -> JevResponse | JevError:
        try:
            return self.jev.ask(request.state, request.questions)
        except JevError as error:
            return error
