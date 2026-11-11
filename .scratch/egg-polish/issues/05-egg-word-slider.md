# 05: The egg word slider

Spec: `.scratch/egg-polish/PRD.md`. Acceptance tests AT-21 to AT-23, AT-25 to AT-29, and AT-38.

**App:** site

**What to build:** One slider replaces the word cards and the won cards of the egg board. A tab row of CORNERSTONE, LANSDALE, and EAGLES, in that fixed order, shows the count of the leader of each word, or "Won". The giant word lights the letters of the leader and outlines the rest. Each open slide keeps the leader line, the top 5 managers with their tiles, and "Show all". A tie says that the managers tie. A won slide is red, lights every letter in red, and shows the winner and the gift card. The slider opens on the closest open race, and a won word goes last. The tabs are a tablist, and the arrow keys move between them. This ticket builds the content with no motion. Ticket 06 adds the motion.

**Blocked by:** 04

**Status:** done

- [x] A board test reads the tab row in the fixed order with the count of each leader, and "Won" for a won word.
- [x] A board test reads the first slide as the open word with the largest share, and a won word as the last slide.
- [x] A board test reads the lit letters and the outlined letters of the giant word from the fixture.
- [x] A board test reads the leader line, the top 5, and the full list after "Show all".
- [x] A board test reads the leader line of a tie, with the teams in the order of the rosters.
- [x] A board test reads the board before any claim: it opens on CORNERSTONE with every letter outlined.
- [x] A board test presses the right arrow on a tab and reads the next tab selected, with the roles tablist, tab, and tabpanel.
- [x] Only a won slide takes the red accent. An open slide sits on the dark hero ground.

## Comments
- Closed by the merge of PR #23.
