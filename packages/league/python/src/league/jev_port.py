"""
The Jev port: one TypeSafe Jev request, a state and a set of Noul questions, with one Jev answer per question key.
TypeSafeJev in jev.py implements it. FakeJev in tests/fakes.py is its one fake.
"""
from dataclasses import dataclass
from typing import Protocol


class JevError(Exception):
    """A Jev request gave no answers: a missing key, an HTTP error, a timeout, or a bad response.

    A caller catches this one type and never reads it as a "no".
    """


@dataclass(frozen=True)
class NoulQuestion:
    """One Noul: a yes or no question, and the situation that each answer means.

    The port owns this shape, so a module that writes the question text never imports the SDK.
    """
    instructions: dict | str
    yes: str
    no: str


@dataclass(frozen=True)
class JevAnswers:
    """The answers of one request: the model id, the probability of yes by question key, and the input tokens."""
    model: str
    nouls: dict[str, float]
    input_tokens: int | None


# The port sits in the provider layer beside the Writer port, so a module of any layer above can take a Jev.
class Jev(Protocol):
    def ask(self, state: dict, questions: dict[str, NoulQuestion]) -> JevAnswers:
        """One request with `state` and every question in `questions`. It gives one answer per key.

        Raises JevError for every failure.
        """
        ...
