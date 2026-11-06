"""
The prose block of one chapter of the midseason report after the state of the league: its key, its title, its facts,
and the teams and players its blurb may name. Each chapter module builds its own, and the prose module writes it.
"""
from pydantic import BaseModel

from league.models import Fact


class ProseBlock(BaseModel):
    """The facts of one more chapter and the scope of its prose block."""
    key: str
    title: str
    facts: list[Fact]
    teams: list[str]
    players: list[str]
