"""
The fact tokens: the number tokens, Nums, and fact. Each package that builds a fact sheet reads them.
Nums records each number as the page shows it, so the verifier can match a sentence number to a cited fact.
"""
import re

from league.models import Fact
from league.numbers import ordinal, r2

# A record such as 33-30 is one token. A leading minus belongs to a negative number.
NUMBER_TOKEN = re.compile(r"\d+-\d+|(?<!\d)-?\d+(?:\.\d+)?|\d+(?:\.\d+)?")
PART_TOKEN = re.compile(r"\d+(?:\.\d+)?")


def fmt(x: float) -> str:
    """Shortest two-decimal form: 106.8 for 106.80, 21 for 21.0."""
    return f"{r2(x):.2f}".rstrip("0").rstrip(".")


class Nums:
    """Formats values for fact text and records each one, so `numbers` is exact."""

    def __init__(self) -> None:
        self.seen: list[str] = []

    def __call__(self, x: float) -> str:
        s = str(x) if isinstance(x, int) else fmt(x)
        self.seen.append(s)
        return s

    def ord(self, n: int) -> str:
        self.seen.append(str(n))
        return ordinal(n)

    def record(self, wins: int, losses: int) -> str:
        self.seen += [str(wins), str(losses), f"{wins}-{losses}"]
        return f"{wins}-{losses}"

    def text(self, raw: str) -> str:
        """Record the numbers in text that code already wrote. Rewrite decimals to the page form."""
        out = PART_TOKEN.sub(
            lambda m: fmt(float(m.group())) if "." in m.group() else m.group(), raw
        )
        for token in NUMBER_TOKEN.findall(out):
            # A record or a negative number also lists its plain parts.
            self.seen += [token, *(p for p in PART_TOKEN.findall(token) if p != token)]
        return out


def fact(fid: str, text: str, n: Nums, teams: list[str], players: list[str]) -> Fact:
    return Fact(id=fid, text=text, numbers=n.seen, teams=teams, players=players)
