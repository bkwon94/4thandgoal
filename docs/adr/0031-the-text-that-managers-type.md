# The text that managers type goes to two vendors, and the miss log stays on Fly

Status: accepted. The spec `front-door` builds it. Brian set the rules on 2026-11-10.

The ask box of the front door takes a question in plain words. Before it, the site sent only data that the pipeline
built. Now a manager can type anything, such as a name, a rude line, or a private fact. The repo is public. We
decided where that text goes and how long we keep it.

## What goes to TypeSafe

Each typed question goes to TypeSafe Jev in one route request (ADR 0029). The request holds:

1. the question as the manager typed it;
2. the 13 Topics, each with a description;
3. the team names of the league;
4. the season, the latest week, and a description of the data sources.

The request holds no roster id, no passphrase, and no name of a manager. TypeSafe does not train on the data. This
account has no zero data retention.

## What goes to Anthropic

A question goes to Claude only on the free answer route and on a personal Topic. Claude gets the question, the
team, and the tool results that it asks for over this season's league data and the nflverse game logs. A refusal and
an honest miss make no Claude call. Anthropic does not train on API data.

## The miss log

1. An honest miss writes one entry: the question as typed, the roster id and the name of Your team, the time, and
   the 3 closest Topics.
2. The log is one SQLite file per client on the Fly volume, at `CORNERSTONE_ASK_DIR`, which is `/data/ask` on Fly.
   It is never in the repo. With no `CORNERSTONE_ASK_DIR`, a local run writes to `data/ask/`, which `.gitignore`
   lists.
3. Each entry stays 90 days. Each write removes the entries older than 90 days.
4. A refusal writes no entry, because its text is the text we least want to keep.

## Considered options

- **Keep the log in the repo, as the tracker notes are.** Rejected because the repo is public, and a question can
  name a person.
- **Keep no log.** Rejected because the commissioner wants to see what managers ask and the site cannot give.
- **Keep each entry for good.** Rejected because an old question has little use, and a kept question is a risk.

## Consequences

- The data that leaves the API grows. A reader finds what leaves, and why, in this record and in ADR 0029.
- The commissioner reads the log on the Fly machine. No route of the API serves it.
- The store holds no Thread and no login. The Thread lives in the browser.
