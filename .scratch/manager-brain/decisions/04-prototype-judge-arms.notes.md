# 04: Notes of the prototype

Ticket: `.scratch/manager-brain/decisions/04-prototype-judge-arms.md`. The prototype script `packages/analyzer/python/prototype_advisor_arms.py` ran on 2026-11-09 and is deleted. These notes keep its questions, tables, and prompt shapes for the spec. The raw results stay outside the repo, because they name the teams of the league.

## Brian's marks

| Arm | Agree, 24 trades | Agree, the 11 split trades |
| - | - | - |
| Jev alone | 17 | 5 |
| Jev atomic | 16 | 4 |
| Claude | 20 | 8 |

## The constants: playbook, voice, Jev questions, tables, cuts

```python
PLAYBOOK = [
    "RBs are worth more this season, because RBs are scarce and the format is half PPR. QBs and TEs are worth the "
    "least, next to RBs and WRs.",
    "A trade is a gut call. Recent trends, recent points, and the coming schedule matter. History helps the gut "
    "call, such as a back who is strong in the second half or in cold weather.",
    "A team that is In firms up its lineup. It makes a big move only when a player of that level becomes available. "
    "A Bubble team or an Out team makes moves and takes more risk to make a push.",
    "One great player is worth two good ones when he is a consensus top 3 to 5 player at his position. The trade "
    "value or the position rank decides who that is each week. The asker decides if the depth is worth the loss.",
    "Managers in this league look a lot at recent points. A slumped star costs less to buy, and a hot player costs "
    "more. This drives the read of whether the other manager would accept.",
    "Upside and the trend of usage matter. A player in line for more work can be worth more than his value now.",
]
VOICE_QUOTE = (
    "Let's say you're trading for Derrick Henry. Maybe you're giving up a player that currently is performing "
    "better, is probably more valued right now based on current performance. Given the situation that Derrick "
    "Henry is in without a starting quarterback, it might be a bit of a risk to trade for him, but historically, "
    "he's been a guy who performs late in the season. If you believe in Derrick Henry, if you believe in that upside "
    "and that potential that he'll bounce back even though he's going through a rough patch, that's something that "
    "is worth considering."
)
VOICE_TAIL = ("At the end of the day, trades are your gut feeling. I want this tool to help push the person in a "
              "certain direction of what they should do on a trade.")
LEAGUE = ("12 teams, half PPR. Each team starts QB, 2 RB, 2 WR, TE, 2 FLEX (RB, WR, or TE), and DEF. "
          "The top 6 teams make the playoffs. Each week has a game and a median game.")

# Inner words of GLOSSARY.md that no bullet and no case may hold.
INNER_WORDS = ["trade value", "highest-value", "best lineup", "the line", "hole", "return bet", "one step",
               "no step", "takes RB", "takes WR", "takes TE", "takes QB", "sits on the bench", "rival"]

# ---------------------------------------------------------------- every Jev question, in one dict

# Each template takes {asker} and {other}. The key is the question id of the request.
ALONE = {
    "send": dict(
        text="Should {asker} send this trade?",
        yes="The trade makes {asker} better for the rest of this season, given its place in the race.",
        no="The trade makes {asker} worse for the rest of this season, or {asker} gives up more than it gets."),
}
# Each atomic question has a weight for the code table. A weight of 0 means the answer is shown but moves nothing.
ATOMIC = {
    "better_now": dict(
        w=2.0, text="Is the best player {asker} gets in this trade better now than the best player {asker} gives?",
        yes="The best player in `trade.asker_gets` scores more and ranks higher this season than the best player in "
            "`trade.asker_gives`.",
        no="The best player in `trade.asker_gives` scores more or ranks higher this season."),
    "fills_need": dict(
        w=1.5, text="Would a player {asker} gets start for {asker} at a position where its starters are weak?",
        yes="A player in `trade.asker_gets` would take a starting spot on `teams.asker` that now has a low-ranked "
            "player or no one.",
        no="Each player in `trade.asker_gets` would sit behind better players on `teams.asker`, or the spot he fills "
           "already has a strong starter."),
    "opens_gap": dict(
        w=-1.5, text="After this trade, does {asker} lack a good starter at a position it starts?",
        yes="After the trade, `teams.asker` has a starting spot with only a low-ranked player or no player for it.",
        no="After the trade, every starting spot of `teams.asker` still has a player who ranks as a starter."),
    "gets_slump": dict(
        w=0.5, text="Is a player {asker} gets in a slump now?",
        yes="A player in `trade.asker_gets` scored well below his season level over the last 3 weeks.",
        no="Each player in `trade.asker_gets` scored near or above his season level over the last 3 weeks."),
    "gets_more_work": dict(
        w=1.0, text="Is a player {asker} gets in line for more work?",
        yes="A player in `trade.asker_gets` has a rising snap share or target share, or a teammate ahead of him is out.",
        no="The snap share and the target share of each player in `trade.asker_gets` are flat or falling."),
    "gives_more_work": dict(
        w=-1.0, text="Is a player {asker} gives in line for more work?",
        yes="A player in `trade.asker_gives` has a rising snap share or target share, or a teammate ahead of him is out.",
        no="The snap share and the target share of each player in `trade.asker_gives` are flat or falling."),
    "history_late": dict(
        w=0.5, text="Do the weeks 9 to 17 splits of past seasons favor the players {asker} gets over the players "
                    "{asker} gives?",
        yes="In the split facts, the players in `trade.asker_gets` scored more points per game in weeks 9 to 17 than "
            "the players in `trade.asker_gives`.",
        no="In the split facts, the players in `trade.asker_gives` scored more in weeks 9 to 17, or one side has no "
           "split."),
    "rb_edge": dict(
        w=1.0, text="Does {asker} get the better running back in this trade?",
        yes="`trade.asker_gets` holds an RB who ranks above every RB in `trade.asker_gives`.",
        no="`trade.asker_gets` holds no RB, or an RB in `trade.asker_gives` ranks above every RB {asker} gets."),
    "star_gets": dict(
        w=1.5, text="Does {asker} get a consensus top 5 player at his position?",
        yes="A player in `trade.asker_gets` is one of the top 5 at his position this season, by his Season rank or "
            "his trade value.",
        no="No player in `trade.asker_gets` is one of the top 5 at his position."),
    "star_gives": dict(
        w=-1.5, text="Does {asker} give up a consensus top 5 player at his position?",
        yes="A player in `trade.asker_gives` is one of the top 5 at his position this season, by his Season rank or "
            "his trade value.",
        no="No player in `trade.asker_gives` is one of the top 5 at his position."),
    "firms_up": dict(
        w=None, text="Does this trade make the starting lineup of {asker} safer for the next few weeks?",
        yes="After the trade, the starters of `teams.asker` score more and depend less on one player.",
        no="After the trade, the starters of `teams.asker` score less or depend more on one player."),
    "swing": dict(
        w=None, text="Is this trade a risky swing for upside for {asker}?",
        yes="{asker} gives steady points now for a player who could score a lot more later, with a real chance he "
            "does not.",
        no="{asker} trades steady points for steady points, with little upside on either side."),
    "accept": dict(
        w=0.0, text="Would the manager of {other} accept this trade?",
        yes="The manager of {other}, who looks a lot at recent points, sees the trade as good for his team.",
        no="The manager of {other} sees the trade as a loss for his team."),
}
# The race group sets the weights of the two race questions: In firms up, Bubble and Out take risks.
RACE_WEIGHTS = {"In": {"firms_up": 1.0, "swing": -0.5}, "Bubble": {"firms_up": 0.5, "swing": 1.0},
                "Out": {"firms_up": 0.0, "swing": 1.0}}
# The code table: a sum of weight * (2p - 1), then these cuts, from the top.
TABLE_CUTS = [(3.0, "Send it"), (1.0, "Lean yes"), (-1.0, "Gut call"), (-3.0, "Lean no")]

# The partner filter asks one Noul per player at a weak starting slot of the other team. Code finds the weak slots.
STARTS_OVER = dict(
    text="Would {player} ({pos}, {nfl}) start over {starter} at {slot} for {team}?",
    yes="{player} would score more points per game than {starter} for the rest of the season.",
    no="{starter} would score as many points per game as {player} or more for the rest of the season.")
FILLS_EMPTY = dict(
    text="Would {player} ({pos}, {nfl}) be a good starter at the empty {slot} spot of {team}?",
    yes="{player} would score like a starter at {slot} for the rest of the season.",
    no="{player} would score below a starter at {slot}.")
FILTER_AT = 0.7      # the TypeSafe default for a yes
# The starter at a slot is weak when his Season rank is past this rank at his position: 12 teams start one QB,
# two RBs, two WRs, one TE, and two FLEX spots.
WEAK_RANK = {"QB1": 12, "RB1": 12, "RB2": 24, "WR1": 12, "WR2": 24, "TE1": 12, "FLEX1": 36, "FLEX2": 36}
SLOT_POS = {"QB1": ("QB",), "RB1": ("RB",), "RB2": ("RB",), "WR1": ("WR",), "WR2": ("WR",), "TE1": ("TE",),
            "FLEX1": ("RB", "WR", "TE"), "FLEX2": ("RB", "WR", "TE")}
TARGET = dict(
    text="Would {team} want {player} ({pos}, {nfl}) from {owner}?",
    yes="{player} would start for {team} or fill a weak spot on its roster.",
    no="{player} would sit behind better players at his position on {team}.")
# The new shortlist questions, with 2 or 3 wordings each for the probe. PICKED names the wording the run uses.
# {team} and {path} name one side: path is `asker` or `partner` under `teams`.
FAIR = {
    "a": dict(text="Is this trade close to fair for both teams: {asker} gives {asker_gives}, and {partner} gives "
                   "{partner_gives}?",
              yes="Each team gives about as much as it gets, by points, rank, and trade value.",
              no="One team gives clearly more than it gets."),
    "b": dict(text="In this trade, {asker} gives {asker_gives} and {partner} gives {partner_gives}. Do both teams "
                   "give up about the same?",
              yes="The players each team gives are about as good as the players it gets.",
              no="The players one team gives are clearly better than the players it gets."),
    "c": dict(text="Would a neutral manager in this league call this trade fair: {asker} gives {asker_gives}, and "
                   "{partner} gives {partner_gives}?",
              yes="A neutral manager says neither team gets robbed.",
              no="A neutral manager says one team gets robbed."),
}
NEED = {
    "a": dict(text="Does {team} fill a starting need in this trade, where it gets {gets}?",
              yes="A player {team} gets would start over a weak starter in `teams.{path}.weak_starting_slots`.",
              no="Each player {team} gets would sit behind the current starters of {team}."),
    "b": dict(text="Would a player {team} gets in this trade, {gets}, start for {team} over one of its weak "
                   "starters?",
              yes="A player {team} gets scores more than a starter listed in `teams.{path}.weak_starting_slots`.",
              no="Each player {team} gets scores less than the weak starters of {team}, or plays another position."),
    "c": dict(text="Does {team} get a player who is better than one of its weak starters in "
                   "`teams.{path}.weak_starting_slots`?",
              yes="A player {team} gets, {gets}, is better than one of those starters at a slot he can fill.",
              no="No player {team} gets, {gets}, is better than those starters at a slot he can fill."),
}
PICKED = {"fair": "a", "need": "a"}
SHORTLIST_KEEP = 10  # the offers per asker that Jev rates highest, by the product of the three new answers
SHORTLIST_OLD = {
    "asker_wants": dict(
        text="Would {asker} want this trade: {asker} gives {asker_gives} and gets {asker_gets}?",
        yes="{asker} ends up with a better team for the rest of the season.",
        no="{asker} ends up with a worse team for the rest of the season."),
    "partner_accepts": dict(
        text="Would the manager of {partner} accept this trade: {partner} gives {partner_gives} and gets "
             "{partner_gets}?",
        yes="The manager of {partner}, who looks a lot at recent points, sees the trade as good for his team.",
        no="The manager of {partner} sees the trade as a loss for his team."),
    "asker_need": dict(
        text="Would a player {asker} gets in this trade start for {asker}: it gets {asker_gets}?",
        yes="A player {asker} gets ranks above a starter of `teams.asker` at his position.",
        no="Each player {asker} gets would sit behind the starters of `teams.asker`."),
    "partner_need": dict(
        text="Would a player {partner} gets in this trade start for {partner}: it gets {partner_gets}?",
        yes="A player {partner} gets ranks above a starter of `teams.partner` at his position.",
        no="Each player {partner} gets would sit behind the starters of `teams.partner`."),
}
TARGET_AT = 0.6      # a player is a target at this probability or more
TARGET_MAX = 4       # at most this many targets per side, by probability
```

## The Claude output models and prompts

```python
class Bullet(BaseModel):
    text: str
    mark: Literal["for", "against", "even"]
    fact_id: str


class AdvisorOut(BaseModel):
    lean: Literal["Send it", "Lean yes", "Gut call", "Lean no", "Pass"]
    case: str
    fairness: Literal["good for both", "fair", "lopsided"]
    lopsided_toward: str | None
    asker_bullets: list[Bullet]
    other_bullets: list[Bullet]


def advisor_system() -> str:
    tips = "\n".join(f"- {t}" for t in PLAYBOOK)
    return f"""You are the Advisor of the cpc fantasy football league. You are a league-mate who advises the asker on one proposed trade. You give an honest read of the other manager too.

The league: {LEAGUE}

The playbook of this league. Where the trade value and the playbook disagree, the playbook wins.
{tips}

Your voice. This is the commissioner's model reply, in his words:
> {VOICE_QUOTE}
And: "{VOICE_TAIL}"

What you give:
1. lean: one of Send it, Lean yes, Gut call, Lean no, Pass, for the asker. A gut call is a real answer for a close trade.
2. case: 3 to 5 sentences to the asker, as "you", in the voice above. Name the risk and the upside, give a condition such as "if you believe X, this is worth it", and push one way. Back claims with the sheet, but do not list stats: at most one number per sentence, and at least one sentence with no number.
3. fairness: "good for both", "fair", or "lopsided". For lopsided, lopsided_toward is the team that gets more. Else it is null.
4. asker_bullets and other_bullets: 3 to 5 bullets per side, one claim each, in plain words. The mark is for, against, or even for that side. fact_id is the one id in `facts` that the claim rests on.

Rules:
- Every number you write must appear in the sheet. A history claim with a number must come from a split fact. With no split, speak of history in words only.
- Say when a split rests on few games.
- Never use these words: {", ".join(INNER_WORDS)}. Say "the other manager" or the team name.
- The Jev answers are quick yes or no reads from a small model. Weigh them, but you make the call.
- Judge as of the week of the trade, with no hindsight."""


def advisor_user(sheet: dict, jev: dict) -> str:
    answers = {fill(ATOMIC[k], asker=sheet["asker"], other=sheet["other"])["text"]: word(p)
               for k, p in jev.items() if k in ATOMIC}
    body = {"asker": sheet["asker"], "other": sheet["other"], "sheet": sheet["state"], "jev_answers": answers}
    return ("Advise the asker on this trade. The sheet holds the trade, both teams, and the facts by id.\n\n"
            + json.dumps(body, indent=1))


NUM = re.compile(r"\d+(?:\.\d+)?")


def check_advisor(out: dict, sheet_text: str, fact_ids: set[str]) -> list[str]:
    allowed = set(NUM.findall(sheet_text))
    fails = []
    texts = [("case", out["case"])] + [(f"{side}[{i}]", b["text"]) for side in ("asker_bullets", "other_bullets")
                                       for i, b in enumerate(out[side])]
    for where, text in texts:
        for n in NUM.findall(text):
            if n not in allowed and n.rstrip("0").rstrip(".") not in allowed:
                fails.append(f"{where}: number {n} is not on the sheet")
        low = text.lower()
        for w in INNER_WORDS:
            if re.search(rf"\b{re.escape(w.lower())}\b", low):
                fails.append(f"{where}: inner word '{w}'")
    for side in ("asker_bullets", "other_bullets"):
        n = len(out[side])
        if not 3 <= n <= 5:
            fails.append(f"{side}: {n} bullets, not 3 to 5")
        for i, b in enumerate(out[side]):
            if b["fact_id"] not in fact_ids:
                fails.append(f"{side}[{i}]: fact id {b['fact_id']} is not on the sheet")
    return fails

# ---------------------------------------------------------------- the Finder


class Pick(BaseModel):
    offer_id: str
    headline: str
    bullets: list[Bullet]


class PickOut(BaseModel):
    picks: list[Pick]
    none_line: str | None


def finder_system() -> str:
    tips = "\n".join(f"- {t}" for t in PLAYBOOK)
    return f"""You are the Advisor of the cpc fantasy football league, in the Finder. You read a shortlist of trades for the asker and pick up to 3 that are good for both sides. The picks share no player.
```
