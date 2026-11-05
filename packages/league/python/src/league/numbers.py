"""
Number helpers for the model layer: rounding, ordinals, and plural words.
One module owns them, so every chapter rounds and spells a number the same way.
"""
from decimal import ROUND_HALF_UP, Decimal


def r2(x: float) -> float:
    """Round half up to two decimals. Python's round() gives 2.78 for 2.785.

    Use it for points and every other value that the page shows to two decimals.
    """
    return float(Decimal(str(x)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def round_half_up(x: float, places: int = 0) -> float:
    """Round half up. Python's round() rounds half to even.

    Use it when the count of places varies, or for a whole-number percent. Use `r2` for two decimals.
    """
    return float(Decimal(str(x)).quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP))


def one_decimal(x: float) -> float:
    """Round half up to one decimal. Python's round() gives 118.7 for 118.75.

    Use it when the caller needs a number to compare or sum. Use `one_decimal_text` for page text.
    """
    return float(Decimal(str(x)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


def one_decimal_text(x: float) -> str:
    """Round half up to one decimal and keep the trailing zero.

    Use it for page text. One decimal is enough for a rate in percentage points, and a fixed form keeps
    "4.0" from reading as a count.
    """
    return f"{round_half_up(x, 1):.1f}"


def ordinal(n: int) -> str:
    """The English ordinal of a whole number: 1st, 2nd, 3rd, 11th."""
    if n % 100 in (11, 12, 13):
        return f"{n}th"
    suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"


def plural(count: int, one: str, many: str) -> str:
    """Pick the word for a count when the plural is not the word plus "s".

    Use it to give only the word. Use `count_noun` to give the count and the word together.
    """
    return one if count == 1 else many


def count_noun(count: int, word: str) -> str:
    """The count and the word together, with a plain "s" for any count but one.

    Use it when the plural is the word plus "s". Use `plural` when it is not.
    """
    return f"{count} {word}" + ("" if count == 1 else "s")
