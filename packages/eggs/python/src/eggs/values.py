"""
The package values of eggs, under [values.eggs] of client.toml.
"make schema" in packages/eggs/python exports the model to values.schema.json beside this file.
"""
from typing import ClassVar

from pydantic import BaseModel, ConfigDict

from league.values import PackageValues


class EggWord(BaseModel):
    """One egg word and the value of its gift card in dollars."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    word: str
    prize: int


# The three egg words of the hunt and their gift cards, in the order of the egg board.
EGG_WORDS = (EggWord(word="CORNERSTONE", prize=50), EggWord(word="LANSDALE", prize=30), EggWord(word="EAGLES", prize=20))


class EggsValues(PackageValues):
    """The package values of eggs: the egg words, the weeks of the hunt, the count of each egg drop, and the roster of
    the commissioner.

    The commissioner places every egg, so the roster of the commissioner cannot hunt. It is a roster id, not a name.
    """

    package: ClassVar[str] = "eggs"

    words: tuple[EggWord, ...] = EGG_WORDS
    first_week: int = 9
    last_week: int = 17
    drop_size: int = 6
    commissioner: int | None = None
