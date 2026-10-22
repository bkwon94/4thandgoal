"""
Player name helpers shared by the blurb verifier, the analysis checks, and the trade analyzer rubric.
It holds the list of name suffixes and the last name of a full name.
"""

NAME_SUFFIXES = {"jr.", "sr.", "ii", "iii", "iv"}


def last_name(full: str) -> str | None:
    parts = [p for p in full.split() if p.lower() not in NAME_SUFFIXES]
    last = parts[-1] if parts else ""
    # Skip short names and odd entries such as "96 (?)": they cause false matches.
    return last if len(last) > 3 and last.isalpha() else None
