"""
The TypeSafe implementation of the Jev port: one System One request over the sync client of typesafe-sdk.
It is the one module that imports the SDK, and it turns every SDK failure into JevError.
"""
from collections.abc import Mapping

from typesafe_sdk import Choice, Noul, NoulCriteria, TypeSafeClient, TypeSafeError

from league.jev_port import ChoiceQuestion, JevError, JevResponse, NoulQuestion

# The alias follows each new Jev release, and each answer saves the exact model id that answered.
MODEL = "jev-latest"


class TypeSafeJev:
    """The Jev port over TypeSafe. With no client, it makes one on its first call, so an import needs no API key.

    The client reads TYPESAFE_API_KEY from the environment. It keeps the default retry of a 429 and a 529.
    """

    def __init__(self, client: TypeSafeClient | None = None):
        self._client = client

    def ask(self, state: dict, questions: Mapping[str, NoulQuestion | ChoiceQuestion]) -> JevResponse:
        """The TypeSafe call of `Jev.ask`. The docstring of the protocol in jev_port.py gives the arguments."""
        typed = {key: Choice(instructions=q.instructions, criteria=dict(q.options)) if isinstance(q, ChoiceQuestion)
                 else Noul(instructions=q.instructions, criteria=NoulCriteria(true=q.yes, false=q.no))
                 for key, q in questions.items()}
        try:
            # One client per adapter: it holds the connection pool. A missing key raises here, on the first call.
            if self._client is None:
                self._client = TypeSafeClient(model=MODEL)
            response = self._client.system_one(state, typed, model=MODEL)
            nouls = {key: response.nouls[key].noul for key, q in questions.items() if isinstance(q, NoulQuestion)}
            choices = {key: dict(response.choices[key].probabilities)
                       for key, q in questions.items() if isinstance(q, ChoiceQuestion)}
        except (TypeSafeError, KeyError) as err:
            # A missing answer is a bad response, so it is the same error as a failed call.
            raise JevError(f"{type(err).__name__}: {err}") from err
        return JevResponse(model=response.model, nouls=nouls, input_tokens=response.usage.input_tokens, choices=choices)


# The one Jev of the process, so the process has one client. The weekly build calls it by default.
JEV = TypeSafeJev()
