# 04: What are the terms of the event, and how do the Finder and the analyzer share one brain?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

Two choices, both about words and voice.

1. The terms. `GLOSSARY.md` lists "banner" as an Avoid word for the Top band, the Hero, the Opener, and the Takeover, and has the Egg banner. It lists "feed" as an Avoid word for the Thread. The spec needs a term for the banner of the event, the live list of trades, the board of needs and spares, and the event as a whole. Proposed: Deadline banner.
2. The shared brain. Brian wants the Finder to share the brain, the perspective, and the writing of the analyzer. Decide what each Finder trade shows: the Lean, the Case, and the Bullets of the Advisor, as the analyzer shows them. Decide if a Finder trade opens in the analyzer in one tap.

## Decision

Brian decided both parts in the grill of 2026-11-18.

**The shared brain.** Each Finder trade is a full read of the Advisor in a short form, in the voice of the analyzer.

1. The Lean leads, as on the analyzer. The Finder shows only Send it, Lean yes, and Gut call. It never shows a trade with Lean no or Pass.
2. The Case follows, at most 3 lines, with the condition first.
3. The Bullets fold under the Case. One tap opens them.
4. The headline goes. The Lean and the Case replace it, so one voice speaks.
5. One tap opens the trade in the analyzer, already graded. The find route sends the read of the Advisor with the trade, so no second grade runs. The manager can edit the trade there and grade it again.

The cost: the pick call writes a Lean and a Case for each trade, about 1 to 2 s more per press.

**The terms.** Written to `GLOSSARY.md`, in the Client language section:

- Deadline week: the event, from its deploy until one day after the Lock.
- Lock: the time when Sleeper closes trades. For CPC it is 00:00 Eastern on Tue 2026-11-24, as one value in `clients/cpc/client.toml`. Brian chose this tight time over 03:00 Eastern. The risk: a trade between the end of the last game and Sleeper's real lock shows after the banner says closed.
- Deadline banner: the strip under the top band, with the countdown to the Lock.
  The countdown carries a caveat, from Brian after the grill: trades stay open until the Monday night games end, with the Lock as the estimate. Example copy: "Trades close after the Monday night games, about 12:00 AM ET." The exact copy waits for prototype 08.
- Trade wire: the live list of trades that Sleeper accepts.
- Deadline board: the page of each team with its race group, needs, and spares.

The entry for Finder document changes to the Lean, the Case, and the Bullets. Site copy still uses plain words, per the rule of no internal names.
