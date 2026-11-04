"""
The chapter keys and fact ID prefixes that the writer and the verifier treat apart, such as the rankings chapter.
The chapters that own these keys import them from here, so each key has one spelling.
"""
from league.models import Chapter, FactSheet

RANKINGS_CHAPTER = "rankings"
# The id prefix of every bye fact. GLOSSARY.md, "Bye line". The writer reads it to add the bye note.
BYE_FACT_PREFIX = "NX.bye."
# The chapters about one or two teams, plus every recap_ chapter. Only these get the hard check on a
# repeated team name: the chapters about every team, such as awards and median, name many teams, and "they" is
# unclear there.
TWO_TEAM_CHAPTERS = ("motw", "game_changer")


def two_team_chapter(key: str) -> bool:
    return key in TWO_TEAM_CHAPTERS or key.startswith("recap_")


def is_motw_recap(chapter: Chapter, sheet: FactSheet) -> bool:
    """True for the recap of the Matchup of the Week pairing.

    Both chapters hold the same matchup facts, so the writer repeats a sentence word for word.
    The check reads the two scopes, so it works on a saved sheet with no rebuild.
    """
    motw = next((c for c in sheet.chapters if c.key == "motw"), None)
    return (motw is not None and chapter.key.startswith("recap_")
            and set(chapter.scope_teams) == set(motw.scope_teams))


def is_game_changer_in_motw(sheet: FactSheet) -> bool:
    """True when the Game Changer plays for a team of the Matchup of the Week.

    The AW.game_changer fact names the team, so the check works on a saved sheet with no rebuild.
    """
    motw = next((c for c in sheet.chapters if c.key == "motw"), None)
    changer = sheet.facts.get("AW.game_changer")
    return motw is not None and changer is not None and bool(set(changer.teams) & set(motw.scope_teams))


def repeats_motw_headline(chapter: Chapter, sheet: FactSheet) -> bool:
    """True for the Matchup of the Week recap, and for game changer and awards when the Game Changer plays in it.

    The game changer or awards chapter then names the same game, so the writer repeats lines such as
    "without X, that is a loss".
    Outside the Matchup of the Week, the note would name a chapter that never told this game.
    """
    if is_motw_recap(chapter, sheet):
        return True
    return chapter.key in ("game_changer", "awards") and is_game_changer_in_motw(sheet)
