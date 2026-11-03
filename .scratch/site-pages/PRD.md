# Site pages: the home, rankings, and analyzer pages per tier

Status: ready-for-agent
Date: 2026-10-27

This is the third of three features that make the site responsive at every width. The
foundation, `.scratch/site-foundation/`, set the tiers, the page column, and the menu. The
report feature, `.scratch/site-report/`, designed the weekly report per tier, with each chapter
as a card on the grey body. This feature designs the home page, the power rankings page, and the
trade analyzer page for a tablet and a desktop, and puts the page shell and the card look in one
place for every page. The terms come from `GLOSSARY.md`. The house rules are
`docs/adr/0006-report-look-at-every-width.md` and `docs/adr/0007-dark-theme-is-one-override-block.md`.

## Problem Statement

A league member opens the home page on a laptop and gets three short chapters stacked in a 720px
column. The first two hold one row each, so most of the column is blank. The gaps between them
come from the thick grey chapter rule, not from the card gap the report uses, so the home page
almost looks like the report and not quite. The power rankings table on a laptop packs ten columns
at the phone widths, with 40px columns and a 4px gap, while the standings on the same screen use
wide tokens. The trade analyzer on a laptop stacks two team pickers and two player lists in one
720px column, so the pick of two teams is a long scroll past rows that use a third of the width.
The result of a trade renders seven thin chapters, two of them one line each. The chapter labels
on the home page are sentence case while the report and the menu are title case.

## Solution

From the tablet tier up, every page renders its chapters as cards on the grey body with the card
gap, through one page shell that the four pages share. On the home page the Tools card and the
Power Rankings card sit side by side, with the Weekly Reports card under them at the full width.
The rankings table gets wide column tokens and a wider gap, as the standings have. The analyzer
form puts the two teams in two columns, the grade button across both, and the result under the
form as five cards. Every chapter label on the three pages is a level-two heading in title case.
The phone keeps each page as it is today. The dark theme holds, because the cards use the same
tokens the report cards use.

## User Stories

### The home page

1. As a league member on a laptop, I want the Tools card and the Power Rankings card side by side, so that the two short chapters fill the column.
2. As a league member on a tablet, I want the same two cards side by side, so that a tablet is not a big phone.
3. As a league member on a phone, I want the home page as it is today, so that the device I read on most does not change.
4. As a league member, I want the Weekly Reports card under the two cards at the full width, so that the list of weeks reads top down, newest first.
5. As a league member, I want one week per row in the list, so that I scan the season in order.
6. As a league member on a laptop, I want the three chapters as white cards on the grey body with an even gap, so that the home page reads as the report does.
7. As a league member, I want the Tools card at the full width when no rankings are published yet, so that the row has no empty half.
8. As a league member, I want the rows to reveal as they do today, so that the home page still arrives as I scroll.
9. As a league member, I want the "Top Three" lead in title case, so that it matches the "Trade Analyzer" lead beside it.

### The power rankings page

10. As a league member on a laptop, I want the ten columns of the rankings table spaced with wide tokens, so that the numbers sit apart as the standings do.
11. As a league member on a tablet, I want the table between the phone spacing and the laptop spacing, so that the step feels even.
12. As a league member, I want the team column wide enough for the longest word of any team name beside the avatar, so that no row grows past the others.
13. As a league member, I want the headers "Stand", "Form", "Sched", and "Pts" at every tier, so that the header row looks the same everywhere.
14. As a league member, I want the method note and the odds note no wider than the measure, so that my eye finds the next line.
15. As a league member on a tablet or a laptop, I want the rankings table as a dark card on the grey body, so that it looks like the standings card of the report.
16. As a league member, I want the week chips, the open row, and the hash link as they are today, so that the page works the same.
17. As a league member, I want the "Power Rankings" label in title case in the table and in the empty state, so that it matches the menu.

### The trade analyzer page

18. As a league member on a laptop, I want My team on the left and The other team on the right, so that I pick two teams without a scroll.
19. As a league member on a laptop, I want each team's player list under its own picker, so that the players I give sit under the team that gives them.
20. As a league member on a tablet, I want the same two columns, so that the form fits one screen.
21. As a league member on a phone, I want the form in one column as it is today, with both pickers before both lists, so that the phone flow does not change.
22. As a league member, I want the grade button across both columns, so that it is one button for the one trade.
23. As a league member, I want the grading status, the error line, and the retry button across both columns under the grade button, so that the state of the grade reads as one line.
24. As a league member on a tablet or a laptop, I want the form in a white card on the grey body, so that the analyzer looks like the rest of the site.
25. As a league member, I want the form card to keep its black "Pick the Teams" heading and take no red label, so that the form reads as a task and not a chapter of a report.
26. As a league member, I want the passphrase dialog as it is today, so that the first visit does not change.
27. As a league member, I want the loading rows, the rate limit line, and the failed fetch line inside the form card, so that every state of the form sits in one place.
28. As a league member, I want the result under the form at the full width of the column, so that the decision, the swap, and the side reads keep their room.
29. As a league member, I want the decision and the fairness line as one card, so that the decision leads and the fairness line sits under it.
30. As a league member, I want the trade swap as one card, each side read as one card, and the counters with the as-of line as one closing card, so that no card holds one line.
31. As a league member, I want the result labels "The Trade" and "Suggested Counters" in title case, so that every label on the site reads the same way.
32. As a league member, I want the trade finder, when its flag is on, under the form across both columns, so that it keeps its place.

### Every page

33. As a league member on a tablet or a laptop, I want every chapter on every page as a card on the grey body, so that the site has one look.
34. As a league member on a phone, I want every page as one unbroken white page with the chapter rules, so that the phone stays as printed.
35. As a league member in the dark theme, I want the cards on the three pages to take the dark partners of their tokens, so that the dark theme holds on every page.
36. As a league member who uses a screen reader, I want each chapter label on the home and rankings pages as a level-two heading, so that I jump from chapter to chapter as I do in the report.
37. As a league member, I want the labels "Tools", "Power Rankings", and "Weekly Reports" in title case, so that the labels match the menu.
38. As a league member on a laptop, I want the week page with its chapter rail as it is today, so that the shared shell changes nothing I see.
39. As a league member, I want no sideways scroll at any width, so that the page never shifts under my thumb.
40. As a league member, I want the three pages to look like the printed report at every tier, so that the black masthead, the red accents, and the type stay the brand.

### The maintainer

41. As the site's maintainer, I want one page shell that renders the grid, the main, and the card gap, so that four pages cannot drift apart.
42. As the site's maintainer, I want the card look of a chapter to hold on every page with no scope attribute, so that a new page gets the look for free.
43. As the site's maintainer, I want the result of the analyzer to use the shared chapter parts, so that one chapter part serves the site.
44. As the site's maintainer, I want the rankings column tokens next to the standings tokens, so that one place sets the table spacing.
45. As the site's maintainer, I want the glossary to name the dark chapter and the card look with one word each, so that a reader of the code and a reader of the glossary agree.
46. As the site's maintainer, I want the tests at the four page seams, so that no test reads a class name.
47. As the site's maintainer, I want a browser pass at 390, 768, and 1280 with a screenshot per page, so that each composition is checked where jsdom cannot.

## Implementation Decisions

### Words

- "Chapter" is the unit on every page. From the tablet tier up a chapter is a card on the grey body. "Card" names that look and nothing else.
- The glossary term "Black card" becomes "Dark chapter", with "black card" in its avoid list. The glossary term "Page" says the surface sits behind the dark chapters. The `card-blk` token keeps its name, because a token is a technical name.
- Every chapter label and heading on the three pages is title case: "Tools", "Power Rankings", "Weekly Reports", "Top Three", "Pick the Teams", "The Trade", "Suggested Counters", and the finder heading. The menu is already title case. The recap buttons stay "Read Recap" and "Hide Recap".

### The page shell

- One shared component, named for the glossary term page column, renders the three-track grid from the tablet tier and the main inside it. The main centers at the page column width, turns clear from the tablet tier, and spaces its chapters with the card gap. The component takes an optional rail, which it places in the left margin track, and the page content as children.
- The week page passes its chapter rail. The home, rankings, and analyzer pages pass no rail, so the left track stays empty and the column stays centered.
- The report scope attribute on the week page's main goes away, and so do the chapter variants that read it. The card look of a chapter, no rule and the page white from the tablet tier, holds on every page.
- The waiver page is behind a flag and stays as it is.

### The home page

- The Tools chapter and the Power Rankings chapter sit in a row with two equal columns from the tablet tier, with the card gap between them. On a phone they stack with the chapter rule as today. The row is one child of the main, so the main's gap applies above and below it.
- With no rankings file, the Tools chapter is the only child of the row and takes the full width.
- The Weekly Reports chapter sits under the row at the full width. One week per row, newest first, as today.
- Each chapter label is a level-two heading. The reveal steps stay as they are.

### The power rankings page

- Wide tokens for the rankings columns from the tablet tier, next to the standings wide tokens, and a wider column gap. The tablet values sit between the phone and the desktop values. The team track must hold the avatar, its gap, and the longest word of any team name at each tier, so no row grows taller than the others. The 480px page tier that unfolds the columns on a phone stays.
- The header names stay short at every tier.
- The method note and the odds note cap at the measure, as every blurb does.
- The table chapter is a dark chapter, so from the tablet tier it is a dark card on the grey body, as the standings are. The label is a level-two heading in the table and in the empty state.

### The trade analyzer page

- The form sits in a chapter, so from the tablet tier it is a white card. The dialog, the loading rows, the rate limit line, and the failed fetch line render inside the same chapter.
- The two pickers and the two player lists sit in a two-column grid from the tablet tier. The pickers take the first row and the lists the second row, each team in its own column, so the document order stays picker, picker, list, list, and the phone flow does not change. The grade button, the grading status, the error line, and the retry button span both columns. The finder, when its flag is on, sits under the form across both columns.
- The result renders under the form. It uses the shared chapter, label, and blurb parts, and its private copies go away. The chapters of the result are: the decision with the fairness line and the no-chart line, the trade swap, one chapter per side read, and the counters placeholder with the as-of line.

### Motion

- No new animation. The reveal and the stagger on the home page, the row reveal in the rankings table, the mount reveal of the form, and the open row stay as they are.

## Testing Decisions

A good test renders a page or a component and reads what a reader sees or a screen reader hears:
roles, names, text, hrefs, and the attributes a reader hears. A test never reads a class name, a
style, a token, or a timing.

The seams are the four page tests that exist, with the real published data and the temp public
folder where they use one today. No new seam.

- The home page test checks the three level-two headings in order, "Tools", "Power Rankings", and "Weekly Reports", the "Top Three" lead, the analyzer link before the weeks, and the Tools chapter with no rankings file.
- The rankings page test checks the "Power Rankings" heading with weeks and in the empty state, and the week line that follows the chips.
- The analyzer test checks both pickers before both lists in document order, the grade button after the lists, and every state of the form, as today.
- The result test checks the labels "The Trade" and "Suggested Counters", the decision text before the fairness text, and the as-of line last.
- The week page test checks the nine chapters, the rail, and the footer as today, so the shared shell proves itself there.

Existing tests that read "Weekly reports", "Power rankings", "Top three", "The trade", or
"Suggested counters" change with the casing.

What the seams cannot check gets a browser pass with agent-browser at 390 by 844, 768 by 1024,
and 1280 by 800, with reduced motion on, in the light theme and the dark theme: the home row of two
cards at 768 and 1280, the stack at 390, the rankings table spacing per tier and the team column
with the longest name, the analyzer form in two columns after a passphrase, the result cards, the
week page unchanged with its rail at 1280, and no sideways scroll. The build and the export check
run before the merge.

## Out of Scope

- Any change to the phone tier of the three pages.
- Any change to the passphrase dialog, the team picker, the player list, or the trade finder beyond their placement.
- A result beside the form. The column is 720px and the result is long.
- Full header names in the rankings table.
- New data on any page.
- Any change to the menu, the sheet, the compact bar, the theme button, or the week page compositions.
- The known issues from the foundation and the report: the level-one heading, the skip link, the theme-color meta, the tap highlight color, the spoken name of the home link, and the hero cutout size.
- Any change under the public folder.

## Further Notes

- Branch `site-pages`, off `main` at the theme merge. Commit nothing on `main`. Rebase onto `main` before the merge, because a week publish lands there.
- The glossary terms in play: chapter, dark chapter, page column, tier, page, theme.
- The design skills to load at build time: `apple-design` and `emil-design-eng` for the compositions, `typeset` for the table spacing, `web-design-guidelines` for the accessibility pass before the merge.
- The team name "Unsolicited Dak Picks" has the longest single word; the rankings table comment records the width it needs at 480px.
