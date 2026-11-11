"""
The TypeSafe implementation of the Jev port: one System One request over the sync client of typesafe-sdk.
It is the one module that imports the SDK, and it turns every SDK failure into JevError.
"""
from collections.abc import Mapping

from typesafe_sdk import Choice, Image, Noul, NoulCriteria, TypeSafeClient, TypeSafeError

from league.jev_port import ChoiceQuestion, JevError, JevImage, JevResponse, NoulQuestion

# The alias follows each new Jev release, and each answer saves the exact model id that answered.
MODEL = "jev-latest"


# The API refuses an image with no opt-in header, because images are experimental.
IMAGES_HEADER = {"TypeSafe-Danger-Zone-Images": "true"}


def has_image(value) -> bool:
    """True if a JevImage sits at any depth of the state."""
    if isinstance(value, JevImage):
        return True
    if isinstance(value, dict):
        return any(has_image(item) for item in value.values())
    if isinstance(value, list):
        return any(has_image(item) for item in value)
    return False


def sdk_state(value):
    """The state with each JevImage, at any depth of dicts and lists, replaced by the SDK image.

    The SDK loads one Image object once and reuses it, so each JevImage gets its own Image.
    """
    if isinstance(value, JevImage):
        return Image(value.png)
    if isinstance(value, dict):
        return {key: sdk_state(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sdk_state(item) for item in value]
    return value


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
            headers = IMAGES_HEADER if has_image(state) else None
            response = self._client.system_one(sdk_state(state), typed, model=MODEL, extra_headers=headers)
            nouls = {key: response.nouls[key].noul for key, q in questions.items() if isinstance(q, NoulQuestion)}
            choices = {key: dict(response.choices[key].probabilities)
                       for key, q in questions.items() if isinstance(q, ChoiceQuestion)}
        except (TypeSafeError, KeyError) as err:
            # A missing answer is a bad response, so it is the same error as a failed call.
            raise JevError(f"{type(err).__name__}: {err}") from err
        return JevResponse(model=response.model, nouls=nouls, input_tokens=response.usage.input_tokens, choices=choices)


# The one Jev of the process, so the process has one client. The weekly build calls it by default.
JEV = TypeSafeJev()
