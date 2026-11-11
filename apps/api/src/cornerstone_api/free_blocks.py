"""
The block of a free answer: a list, a table, or a player card that Claude shows under its lead line through the display
tool, and the plain sentence of each row, so the Jev check reads a block as it reads the text.
"""
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, model_validator

# The caps of a block. A block fits the Answer card of a phone, so a long table or a long label cannot reach the page.
ROWS_MAX = 12
COLUMNS_MAX = 4
STATS_MAX = 4
LABEL_MAX = 40
TAG_MAX = 12
VALUE_MAX = 24
NOTE_MAX = 120

Label = Annotated[str, Field(min_length=1, max_length=LABEL_MAX)]
Value = Annotated[str, Field(min_length=1, max_length=VALUE_MAX)]
Note = Annotated[str, Field(min_length=1, max_length=NOTE_MAX)]


class _Shape(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ListRow(_Shape):
    """One ranked row: the rank, the player or the team, a small tag such as the position, the value, and a short note."""

    rank: int = Field(ge=1, le=99)
    name: Label
    tag: Annotated[str, Field(min_length=1, max_length=TAG_MAX)]
    value: Value
    note: Note | None = None


class ListBlock(_Shape):
    """A ranked list, such as the players of a team by season points. `title` says what the value is."""

    kind: Literal["list"]
    title: Label
    rows: list[ListRow] = Field(min_length=1, max_length=ROWS_MAX)


class TableBlock(_Shape):
    """A small table for a comparison: 2 to 4 columns, and one cell per column in each row."""

    kind: Literal["table"]
    title: Label
    columns: list[Label] = Field(min_length=2, max_length=COLUMNS_MAX)
    rows: list[list[Value]] = Field(min_length=1, max_length=ROWS_MAX)

    @model_validator(mode="after")
    def _cells(self) -> "TableBlock":
        if any(len(row) != len(self.columns) for row in self.rows):
            raise ValueError(f"Each row needs exactly {len(self.columns)} cells, one per column.")
        return self


class Stat(_Shape):
    label: Label
    value: Value


class PlayerBlock(_Shape):
    """One player: the name, the position, the NFL team, the fantasy team or None for a free agent, whether he can play
    now with the status of the injury report, up to 4 stats, and a short note."""

    kind: Literal["player"]
    name: Label
    position: Annotated[str, Field(min_length=1, max_length=TAG_MAX)]
    nfl_team: Annotated[str, Field(min_length=1, max_length=TAG_MAX)] | None = None
    fantasy_team: Label | None = None
    can_play_now: bool
    status: Annotated[str, Field(min_length=1, max_length=TAG_MAX * 2)]
    stats: list[Stat] = Field(default_factory=list, max_length=STATS_MAX)
    note: Note | None = None


# The kind picks the shape, so a bad block fails its validation in the display tool and never reaches the page.
Block = Annotated[ListBlock | TableBlock | PlayerBlock, Field(discriminator="kind")]
BLOCK = TypeAdapter(Block)

# What a row sentence of the check means. It rides in the check state beside the rows, so the check reads the block
# as the manager does (ticket 26).
BLOCK_MEANING = ("Each sentence of `answer` that starts with \"Row\" or \"The player card\", or with a player name and a "
                 "colon, is one row of a block that the site shows under the text, as a plain sentence. A list row "
                 "is its rank, its name, a small tag such as the position or the NFL team, and its value, which the "
                 "title of the list names, such as \"Season points\". A table row gives the cell of each column by "
                 "the column name. The player card gives the player, his position, his NFL team, his fantasy team, "
                 "and whether he can play now with his injury status, then one sentence per stat.")


def row_sentences(block: Block | None) -> list[str]:
    """Each row of `block` as one plain sentence, such as "Row 1 of the list "Season points": Kenneth Walker III, RB,
    142.3." A player card gives its head, one sentence per stat, and its note."""
    if block is None:
        return []
    if isinstance(block, ListBlock):
        return [f"Row {row.rank} of the list \"{block.title}\": {row.name}, {row.tag}, {row.value}."
                + (f" {row.note}" if row.note else "") for row in block.rows]
    if isinstance(block, TableBlock):
        return [f"Row {number} of the table \"{block.title}\": "
                + "; ".join(f"{column}: {cell}" for column, cell in zip(block.columns, row)) + "."
                for number, row in enumerate(block.rows, start=1)]
    team = f"on {block.fantasy_team}" if block.fantasy_team else "a free agent"
    play = "can play now" if block.can_play_now else "cannot play now"
    head = ", ".join(part for part in (block.name, block.position, block.nfl_team, team) if part)
    return [f"The player card: {head}, {play} ({block.status}).",
            *(f"{block.name}: {stat.label} {stat.value}." for stat in block.stats),
            *([block.note] if block.note else [])]
