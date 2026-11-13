# week: the weekly report of one league

## Knows

- The [sheet owner](python/src/week/sheet/README.md) holds roster projections. The sheet chapters except rankings, the league and matchup facts, and the page writer of `page.json` (`cpc-week`, imported as `week`).
- The week chapters, the schema and the types of `page.json`, and `who` (`@cpc/week`). The loader of `page.json` stays in the site app, because it reads files.
- The median text in `prompts/median.md`. The writer and the verifier get it only when the league scores a median game.
- A league with no median game has no MED facts, no median part in the impact fact, and no Median Game chapter.
- The tunables of the week in `tunables.py`: the shootout cut, the storyline weights, the key starter rule, and the award cap.
- Package values: it has no values.

## Ports

- The chapter port `ChapterSource` in `sheet/port.py`: a chapter of another package, with its facts and the odds it computes. The app passes the source of each package that the client takes, so a client with no rankings has no rankings chapter and no odds.
- The registry of the site build lists the home chapter of each package that the client takes, and no other. Each one sits in `apps/site/src/app/_routes/<package>/home.tsx`.

## Does not do

- It imports no app and no core package, only `league` and `facts`. `tests/test_layers.py` of the pipeline checks it.
- It holds no odds engine and no power rankings. The [rankings owner](../rankings/README.md) gives them through the chapter port. Roster projections belong to the sheet, not that odds engine.
- It writes no rankings, managers, or waiver file. Each package writes its own.
- It sends no Claude call of its own. The writer and the verifier of `facts` write and check each blurb.
