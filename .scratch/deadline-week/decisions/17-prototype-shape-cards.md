# 17: How do the new shapes look in the pick, the wait, and the cards?

Map: `.scratch/deadline-week/MAP.md`.

**Kind:** prototype

**Blocked by:** 16

**Status:** done

## Question

A 2-for-1, a 3-for-1, or a 3-for-2 offer has more players than the 1-for-1 cards of ticket 07. Brian must see it before the choice. Decide:

1. How the pick call and the A to J labels name a multi-player offer, and how many picks and near ideas it shows. Today it shows up to 3 of each (`finder_pick.py:52-54`), and the Finder now aims at varied ideas.
2. How the step lines of the stream read with the new sources.
3. How a card of ticket 07 shows each shape on the phone, at 390x660, and on tablet and desktop (memory `iphone-real-viewport`).

Site copy never names Jev, Advisor, Finder, front door, or Brian (memory `no-internal-names`).

## Decision

Brian chose on 2026-11-19, on the phone, from three cards: A · Ledger, B · Balance, and C · Lead line. The prototype is on the branch `deadline-week-17-proto` at `c403b55f`. It mounts the cards in the real Finder result area, with the real week 11 offers of Bo Girds. It stays off `main` as the primary source.

1. **The card is A · Ledger.** Two columns, "You get · N" and "You give · N". Each player row shows the name, the position, the NFL team, and the rank, such as "RB · DAL · RB8". Under each column sits its trade value total. A 3-for-2 stays clean, because a column just grows a row.
2. **One plain gap line from B.** Under the two totals, one line states the gap, such as "You get 9% more trade value".
3. **No trade value on a player row.** The rank carries the signal. The full result after a tap shows each value.
4. **5 picks,** with up to 3 near ideas folded under them as "Close, but not sent · N". `MAX_PICKS` goes from 3 to 5. The pick call can show fewer when fewer are good.
5. **The wait lines,** each with the "n of 5 ·" prefix of the real wait, and the numbers of each real press:
   1. Reading 11 teams
   2. Matching trade value
   3. Checking 4,667 trades for fairness
   4. Checking 77 against both lineups
   5. Picking the best 5
6. **The A to J labels stay.** A letter names a whole offer, and the Shortlist stays at 10.
7. The card keeps the Lean, the Case of up to 3 lines, the folded Bullets, and "See the Full Result" of decision 07.

**For the spec.** The real wait shows "This can take about 25 seconds." That breaks the rule against a time claim (memory `no-time-claims`). The prototype used "Who has a trade for you?" in its place. The spec removes the time claim.
