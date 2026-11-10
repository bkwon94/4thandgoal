"""
Player name helpers shared by the blurb verifier, the Advisor guards, and the Measures of the trade analyzer.
It holds the list of name suffixes, the name particles, and the last name of a full name.
"""

NAME_SUFFIXES = {"jr.", "sr.", "ii", "iii", "iv"}

# A word that joins the last word to make one last name, such as "St." in "Amon-Ra St. Brown".
# To a reader, "Brown" alone names a different player. A chain such as "De La Cruz" keeps the last word only.
NAME_PARTICLES = ("st.", "st", "saint", "van", "vander", "de", "del", "von")


def last_name(full: str) -> str | None:
    parts = [p for p in full.split() if p.lower() not in NAME_SUFFIXES]
    last = parts[-1] if parts else ""
    # Skip short names and odd entries such as "96 (?)": they cause false matches.
    if not (len(last) > 3 and last.isalpha()):
        return None
    # Only a middle word can be a particle: in "Van Jefferson" the "Van" is a first name.
    if len(parts) > 2 and parts[-2].lower() in NAME_PARTICLES:
        return f"{parts[-2]} {last}"
    return last
