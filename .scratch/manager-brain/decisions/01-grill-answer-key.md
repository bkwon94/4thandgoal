# 01: Which trades make the answer key

Map: `.scratch/manager-brain/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The prototype of ticket 04 needs about 30 trades with a known answer. The sets: about 10 real league trades from the Sleeper transactions, about 10 week 8 Finder trades with Gibbs for Bijan and Henry for Tuten and Higgins, and about 10 made-up trades: robberies, close calls, and trades between a contender and a seller. Brian grades all 30: yes, no, or not as is, with one line of why. A real trade is not a yes by itself, because managers make bad trades. Its acceptance labels only the question "would the other manager accept?". The key names managers, so it stays in `.scratch/` (ADR 0021). The why lines also guide the voice of the judge.

## Decision

Brian decided on 2026-11-09 to drop a written key. He gives a playbook, and he reacts to the prototype output.

1. **The test set.** It has 30 trades in `01-grill-answer-key.notes.md`, each with a context block of the stats as of its week. Set 1 has 10 real cpc trades from weeks 2 to 7. Set 2 has 10 week 8 Finder trades, with Gibbs for Bijan (11) and Henry for Tuten and Higgins (12). Set 3 has 10 trades that Claude made up. Week 1 trades have no snapshot before them, so they are out.
2. **The frame.** A trade is judged for the asker, the team named first, as of its week, with no hindsight. A real trade is not a yes by itself. Its acceptance labels only "would the other manager accept?".
3. **The key comes from reactions.** In ticket 04 each arm gives a lean and a case for each trade. Brian marks agree or disagree where the arms disagree, or where a read looks wrong. His marks are the key. A written grade of 30 trades took too long, and neither model learns from it.
4. **The lean.** The hero shows one of five leans: Send it, Lean yes, Gut call, Lean no, or Pass. The case sits under it. A gut call is a real answer for a close trade.
5. **The voice.** The judge advises like a manager. It weighs the case, names the risk and the upside, and gives a condition: "if you believe in X, this is worth it". It backs its claims with data, but it does not list stats. Brian's model reply, in his words:

   > Let's say you're trading for Derrick Henry. Maybe you're giving up a player that currently is performing better, is probably more valued right now based on current performance. Given the situation that Derrick Henry is in without a starting quarterback, it might be a bit of a risk to trade for him, but historically, he's been a guy who performs late in the season. If you believe in Derrick Henry, if you believe in that upside and that potential that he'll bounce back even though he's going through a rough patch, that's something that is worth considering.

   And: "At the end of the day, trades are your gut feeling. I want this tool to help push the person in a certain direction of what they should do on a trade."
6. **The playbook.** Each client has a playbook file in its voice folder that the judge reads. The cpc playbook, from Brian:
   - RBs are worth more this season, because RBs are scarce and the format is half PPR. QBs and TEs are worth the least, next to RBs and WRs.
   - A trade is a gut call. Recent trends, recent points, and the coming schedule matter. History helps the gut call, such as Henry in the second half and in cold weather, or Chase Brown in the second half.
   - A contender firms up its lineup. It makes a big move only when a player of that level becomes available. A bubble team or a low team makes moves and takes more risk to make a push.
   - One great player is worth two good ones when he is a consensus top 3 to 5 player at his position. The chart value or the position rank decides who that is each week. Gibbs, Kenneth Walker, JSN, and Puka are examples for 2026. The asker decides if the depth is worth the loss.
   - Managers in this league look a lot at recent points. A slumped star costs less to buy, and a hot player costs more. This drives the read of "would he accept?".
   - Upside and the trend of usage matter. A player in line for more work can be worth more than his value now.
7. **History.** The fact sheet gets past-season splits, such as weeks 1 to 8 against weeks 9 to 17, so a history claim has a number that a check can confirm. Where the sheet has no history, Claude may use what it knows of football, but with no number. The guard blocks any number that is not on the sheet. Ticket 06 finds the source of the splits.
