"""
The TypeSafe implementation of the Jev port: one System One request over the sync client of typesafe-sdk.
It is the one module that imports the SDK, and it turns every SDK failure into JevError.
"""
from typesafe_sdk import Noul, NoulCriteria, TypeSafeClient, TypeSafeError

from league.jev_port import JevError, JevResponse, NoulQuestion

# The alias follows each new Jev release, and each answer saves the exact model id that answered.
MODEL = "jev-latest"


class TypeSafeJev:
    """The Jev port over TypeSafe. With no client, it makes one on its first call, so an import needs no API key.

    The client reads TYPESAFE_API_KEY from the environment. It keeps the default retry of a 429 and a 529.
    """

    def __init__(self, client: TypeSafeClient | None = None):
        self._client = client

    def ask(self, state: dict, questions: dict[str, NoulQuestion]) -> JevResponse:
        """The TypeSafe call of `Jev.ask`. The docstring of the protocol in jev_port.py gives the arguments."""
        nouls = {key: Noul(instructions=q.instructions, criteria=NoulCriteria(true=q.yes, false=q.no))
                 for key, q in questions.items()}
        try:
            # One client per adapter: it holds the connection pool. A missing key raises here, on the first call.
            if self._client is None:
                self._client = TypeSafeClient(model=MODEL)
            response = self._client.system_one(state, nouls, model=MODEL)
            answers = {key: response.nouls[key].noul for key in questions}
        except (TypeSafeError, KeyError) as err:
            # A missing answer is a bad response, so it is the same error as a failed call.
            raise JevError(f"{type(err).__name__}: {err}") from err
        return JevResponse(model=response.model, nouls=answers, input_tokens=response.usage.input_tokens)


# The one Jev of the process, so the process has one client. The weekly build calls it by default.
JEV = TypeSafeJev()
