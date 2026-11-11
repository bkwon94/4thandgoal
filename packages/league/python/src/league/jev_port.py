"""
The Jev port: one TypeSafe Jev request, a state and a set of Noul and Choice questions, with one answer per question key.
TypeSafeJev in jev.py implements it. FakeJev in tests/fakes.py is its one fake.
"""
from collections.abc import Mapping
from dataclasses import dataclass, field
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
class ChoiceQuestion:
    """One Choice: a question, and a description of each option by its key. Jev picks one option.

    A Choice always picks an option, even when none fits, so a caller pairs it with a Noul that asks whether one fits.
    """
    instructions: dict | str
    options: dict[str, str]


@dataclass(frozen=True)
class JevImage:
    """A PNG image that a state holds, as bytes.

    The port owns this type, so a caller never imports the SDK. The API takes 280 to 1568 px per side and never
    resizes, so the caller cuts or scales a shot first.
    """
    png: bytes


@dataclass(frozen=True)
class JevResponse:
    """The answers of one request: the model id, the probability of yes by Noul key, and the input tokens.

    `choices` holds the probability of each option by Choice key. A request with no Choice leaves it empty.
    """
    model: str
    nouls: dict[str, float]
    input_tokens: int | None
    choices: dict[str, dict[str, float]] = field(default_factory=dict)


# The port sits in the provider layer beside the Writer port, so a module of any layer above can take a Jev.
class Jev(Protocol):
    def ask(self, state: dict, questions: Mapping[str, NoulQuestion | ChoiceQuestion]) -> JevResponse:
        """One request with `state` and every question in `questions`. It gives one answer per key: a Noul key in
        `nouls`, and a Choice key in `choices`.

        Raises JevError for every failure.
        """
        ...
