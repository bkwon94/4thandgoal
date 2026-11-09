# 03: How do the egg word cards show the race after Stack Slider?

Map: `.scratch/egg-polish/MAP.md`.

**Kind:** grill

**Blocked by:** none

**Status:** done

## Question

The egg board has one card per egg word now. Stack Slider shows one giant word per slide and swaps the title letter by letter. The spec needs what each slide shows: the letters of each manager, the leader, the winner of a won egg word, and the order on a phone.

## Decision

The egg word cards become one slider after Stack Slider, with a tab row above it. Brian decided each part in a grill on 2026-11-08.

1. The slider shows one egg word per slide. A swipe or a tap of a tab moves to another word, and the giant title swaps letter by letter.
2. A tab row of the three words sits above the slider. Each tab shows the count of the leader, such as "CORNERSTONE 4/11", so the race stays in view.
3. The giant word lights each letter the leader holds in white. Each letter the leader still needs is a dim outline.
4. A won word lights every letter in red. The name of the winner and the gift card show under it.
5. Under the giant word, each slide keeps the leader line, the top 3 managers with their tiles, and "Show all", which opens the full list in place.
6. The closest open race opens first: the open word whose leader holds the largest share of its letters. The other open words follow, closest first.
7. A won word goes last. A tie in the share keeps the fixed order. The tabs always keep the fixed order CORNERSTONE, LANSDALE, EAGLES.
8. An open word sits on the dark hero ground. A won word washes the frame into the red accent. No word gets a new color.

Brian chose the slider over three cards in view, because the tab row keeps the glance. Brian chose no tint for each word, because the brand has one accent.
The spec records the small calls, such as the leader line for a tie.
