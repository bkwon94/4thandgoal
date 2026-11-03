# Read the trade value chart from its image

The trade value chart Brian trusts, the half-PPR redraft chart at peakedinhighskool.com, exists
only as a weekly PNG. The site has no table, CSV, or API, and the Patreon tier gives the redraft
chart as an image too. We read the image with Claude vision once a week, cache the parsed values
per week, and refuse the read when a guard fails: the header week must match, trade values must
never rise down the sheet, every trade value must be a half point from 0 to 100, every position
must be RB, WR, TE, or QB, the sheet must hold at least 100 rows, rows that two strips both hold
must agree, and the row count must stay near the prior week's.

## Considered Options

- FantasyCalc's JSON API: free, Sleeper IDs on every row, but a different chart built from market
  trades. Rejected because Brian chose this author's chart.
- A dynamic site that renders values live: does not help, because the source is a picture either
  way.

## Consequences

- A misread digit cannot land on the page. Trade values never appear in the prose or on the card.
  They shape the grade only, so a misread nudges an opinion and nothing more.
- The chart for week N is the file whose date falls in the week N trade window, so a rebuilt week
  uses the chart of its own week.
- The build never fails on the chart. An outage or a failed guard means no value facts that week.
