"""
The egg file of the commissioner: each proposed spot of the hunt, with its week, its reason, and its confirmed mark.
The file sits outside the public repo, at ~/cpc-eggs/<season>.toml by default, so the repo never names a spot.
"""
import json
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


class EggFileError(ValueError):
    """The egg file is not valid. The message names the file and the problem."""


def default_egg_file(season: int) -> Path:
    """The egg file of the season on the laptop of the commissioner, outside the repo."""
    return Path.home() / "cpc-eggs" / f"{season}.toml"


@dataclass(frozen=True)
class Spot:
    """One spot of the egg file: where an egg hides, the action and the conditions that find it, and why it is there.

    Only a spot that the commissioner marks confirmed can drop.
    """

    week: int
    page: str
    target: str
    action: str
    reason: str
    conditions: dict[str, Any] = field(default_factory=dict)
    confirmed: bool = False

    def egg(self) -> dict[str, Any]:
        """The egg of the spot as the drop route takes it. The reason and the mark stay in the file."""
        return {"page": self.page, "target": self.target, "action": self.action, "conditions": self.conditions}


def read_spots(path: Path) -> list[Spot]:
    """Each spot of the egg file, in the order of the file. A file that does not exist holds no spot.

    A file that is not valid TOML, or a spot with a missing or wrong field, raises EggFileError.
    """
    if not path.is_file():
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as err:
        raise EggFileError(f"The egg file {path} is not valid TOML: {err}") from err
    return [_spot(path, number, each) for number, each in enumerate(data.get("eggs", []), start=1)]


def _spot(path: Path, number: int, each: dict[str, Any]) -> Spot:
    for name in ("week", "page", "target", "action"):
        if name not in each:
            raise EggFileError(f"The egg file {path} has no {name} in egg {number}.")
    try:
        return Spot(week=int(each["week"]), page=each["page"], target=each["target"], action=each["action"],
                    reason=each.get("reason", ""), conditions=dict(each.get("conditions", {})),
                    confirmed=bool(each.get("confirmed", False)))
    except (TypeError, ValueError) as err:
        raise EggFileError(f"The egg file {path} has a wrong value in egg {number}: {err}") from err


def confirmed_spots(path: Path, week: int) -> list[Spot]:
    """The spots of the week that the commissioner confirmed. Only these drop."""
    return [spot for spot in read_spots(path) if spot.week == week and spot.confirmed]


def append_spots(path: Path, spots: list[Spot]) -> None:
    """Add the spots at the end of the egg file. The text already in the file stays as the commissioner wrote it."""
    path.parent.mkdir(parents=True, exist_ok=True)
    before = path.read_text(encoding="utf-8") if path.is_file() else ""
    path.write_text(before + "".join(_table(spot) for spot in spots), encoding="utf-8")


def _table(spot: Spot) -> str:
    conditions = ", ".join(f"{_key(name)} = {_value(value)}" for name, value in spot.conditions.items())
    return (f"\n[[eggs]]\nweek = {spot.week}\npage = {_value(spot.page)}\ntarget = {_value(spot.target)}\n"
            f"action = {_value(spot.action)}\nconditions = {{ {conditions} }}\nreason = {_value(spot.reason)}\n"
            f"confirmed = {_value(spot.confirmed)}\n")


def _key(name: str) -> str:
    # A bare TOML key holds only letters, digits, "_", and "-". Each other key goes in quotes.
    return name if re.fullmatch(r"[A-Za-z0-9_-]+", name) else _value(name)


def _value(value: Any) -> str:
    # A JSON string, number, or bool is also a valid TOML value, so json.dumps writes each one.
    # A JSON array of such values is a valid TOML array, so a list of them goes the same way.
    if isinstance(value, (str, bool, int, float)):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(_value(item) for item in value) + "]"
    raise ValueError(f"An egg file value must be a string, a number, or a bool, not {value!r}.")
