# league: the shared kernel of every client

## Knows

- The models, the client and its League settings, the paths, the history, nflverse, the snapshot, the lineup, the model of the matchup card, the standings table, the chart, and the shared tunables (`cpc-league`, imported as `league`).
- The headshot, the avatar, their default images, the Sleeper CDN headshot URL, and the manager page hrefs of the site (`@cpc/league`).
- The Sleeper player ID is the one canonical player ID. Each other source maps its own ID to it, as `nflverse` does with the gsis ID.
- The reception points of the League settings choose the points key: 0 gives `pts_std`, 0.5 `pts_half_ppr`, 1 `pts_ppr`.
- The roster slots set the pool and the leader positions. A position with no slot, through a flex slot too, is out of both.
- Package values, under `[values.league]`: `chart`, the name of the trade value chart. The default is no chart, and then each chart value is 0.

## Ports

- `Provider` in `provider/base.py`: the fetches of a league service. `SleeperProvider` takes its cache dir in its constructor.
- `Writer` in `claude_port.py`: the one Claude call. Every outside service enters the league package: Sleeper, nflverse, the chart, Claude, and TypeSafe.
- `Jev` in `jev_port.py`: the one TypeSafe call, with Noul and Choice questions. `TypeSafeJev` in `jev.py` is the adapter, and it reaches TypeSafe.
- The port still carries these Sleeper shapes. A later adapter must map each one: the raw week files of `provider/raw.py`, the roster and matchup ids, the transaction legs, the stat lines keyed by `pts_*`, the players file, the trending adds, and the league file.

## Does not do

- It imports no app and no other package. `tests/test_layers.py` of the pipeline checks it.
- It holds no rule of one core package. A term of one package stays in that package (decision 01).
- It writes no published file. Each package writes its own.
