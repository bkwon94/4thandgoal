"""
The Jev requests of one press, sent in waves under the TypeSafe rate limits of requests and tokens per second.
Each wave runs its requests at once. A wave goes at once while the last second has room for its count of requests and
tokens, and it waits only for the room. Every press of the process shares one pacer for that room.
"""
import json
import logging
import math
import threading
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from league.jev_port import Jev, JevError, JevResponse, NoulQuestion

log = logging.getLogger(__name__)

# The limits of the TypeSafe account, from its dashboard: 80 requests per second and 100,000 tokens per second.
REQUESTS_PER_SECOND = 80
TOKENS_PER_SECOND = 100_000
# The context of one Jev request. A larger request fails, so a caller splits its questions into requests under it. The
# long-context header of TypeSafe lifts the limit, and Brian chose the split over it (decision 14).
REQUEST_TOKENS = 64_000
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


class Pacer:
    """The budget of the TypeSafe account for one second: the start time, the requests, and the tokens of each wave of
    the last second.

    TypeSafe counts the limits for the whole account, so every press of one process shares the one PACER. Two
    presses with a pacer each could pass the limit together (decision 16). The Fly app runs one process.
    """

    def __init__(self, clock: Callable[[], float] = time.monotonic, sleep: Callable[[float], None] = time.sleep):
        self.clock = clock
        self.sleep = sleep
        # The start time, the requests, and the tokens of each wave that started less than one second ago.
        self._sent: list[tuple[float, int, int]] = []
        self._lock = threading.Lock()

    def reserve(self, count: int, tokens: int) -> None:
        """Wait until the last second has room for `count` more requests and `tokens` more tokens, then count them.

        The check and the count happen under one lock, so two threads never take the same room. The wait happens
        outside it, so one waiting press never stops the clock of another.
        """
        while True:
            with self._lock:
                now = self.clock()
                self._sent = [wave for wave in self._sent if wave[0] + WAVE_SECONDS > now]
                if (sum(wave[1] for wave in self._sent) + count <= REQUESTS_PER_SECOND
                        and sum(wave[2] for wave in self._sent) + tokens <= TOKENS_PER_SECOND):
                    self._sent.append((now, count, tokens))
                    return
                # The oldest wave leaves the second first, so its end is the soonest time that can make room.
                wait = self._sent[0][0] + WAVE_SECONDS - now
            self.sleep(wait)


# The one pacer of the process. Each JevWaves uses it unless a test gives its own.
PACER = Pacer()


class JevWaves:
    """The Jev requests of one press, in waves under the budget of the shared pacer.

    So the partner filter, the targets, and the shortlist of every press share one budget per second, as TypeSafe
    counts it. A press sends about 11 requests and 27k tokens per wave, so a wave seldom waits (decision 02).
    """

    def __init__(self, jev: Jev, pacer: Pacer = PACER):
        self.jev = jev
        self.pacer = pacer
        self.waves_sent = 0

    def ask(self, requests: dict[str, WaveRequest], label: str,
            answered: Callable[[str], None] | None = None) -> dict[str, JevResponse | None]:
        """The answer of each request by key. A failed request gives None, and it logs, so one failure never stops
        the press. A caller never reads None as a no.

        With `answered`, each key goes to it as its request ends, in the order the answers come, so a stream can
        report each read as it happens. A failed request is read too, because the press is done with it.
        """
        answers: dict[str, JevResponse | None] = {}
        for keys in plan_waves(requests):
            tokens = sum(estimated_tokens(requests[key]) for key in keys)
            self.pacer.reserve(len(keys), tokens)
            self.waves_sent += 1
            log.info("Jev wave %d (%s): %d requests, about %d tokens", self.waves_sent, label, len(keys), tokens)
            with ThreadPoolExecutor(max_workers=len(keys)) as pool:
                futures = {key: pool.submit(self._one, requests[key]) for key in keys}
                if answered is not None:
                    keys_of = {future: key for key, future in futures.items()}
                    for future in as_completed(keys_of):
                        answered(keys_of[future])
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
