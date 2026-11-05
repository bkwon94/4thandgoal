# rankings: the power rankings and the playoff odds

## Knows

- The power rankings in `power_rankings.py`, the playoff odds engine in `odds.py`, and the numbers of `tunables.py` (`cpc-rankings`, imported as `rankings`).
- The rankings chapter, the odds facts, the power facts, and the why facts in `chapter.py`. The writer of `rankings.json` in `published.py`.
- A league with no median game counts one game a week in the records, the clinch check, and the odds. Its power form has no median weight.
- The power rankings Ladder, the week choice, the top three of the home page, the schema and the types of `rankings.json`, and its fixture (`@cpc/rankings`). The loader of `rankings.json` stays in the site app, because it reads files.
- Package values: it has no values.

## Ports

- `RANKINGS` in `chapter.py` implements `ChapterSource`, the chapter port of the week. It gives the week the rankings chapter, its facts, and the odds.
- `Context` in `chapter.py` names the part of the week context that the rankings reads, so the package imports no week code.

## Does not do

- It imports no app and no other core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It builds no week chapter and writes no `page.json`. The week package does both.
- It sends no Claude call of its own. The writer and the verifier of `facts` write and check the rankings blurb.
