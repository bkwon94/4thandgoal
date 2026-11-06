# The evidence

Stage 3 of `cpc:implement`. Record the evidence of each acceptance test `AT-<n>` of `.scratch/<slug>/ACCEPTANCE.md`. The evidence uses real data and a real build, with no mock (ADR 0020).

The evidence states what the instrument showed. It holds no PASS, no FAIL, and no BLOCKED. Only the Judge gives a Test verdict, in stage 4 (ADR 0026).

## Before the first test

1. Start after the last commit of stage 2, so that each file shows the head commit. Write down `git rev-parse --short HEAD`.
2. Skip a test whose ticket is `blocked`, or is behind a `blocked` ticket. Its entry in `EVIDENCE.md` names the ticket.
3. Skip a test with the word `Retired` in its title.

## The background check

Decision 05 sets one full check for each spec. It adds no wall time, because the evidence stage takes longer than the check.

1. Start it first, before the first test. Run `make check` in the Spec worktree with the Bash tool `run_in_background`. Write the output to a log file outside the repo, such as `make check > <scratchpad>/<slug>-check.log 2>&1`. Use the session scratchpad if one exists, else `/tmp/<slug>-check.log`. A log in the repo is an untracked file, so the first step of stage 4 fails and the log can get into an evidence commit.
2. Write down the start time.
3. Do not start the evidence of a test until the run is live.

**One `uv run` for each checkout.** Run no other `uv run --exact --package` in the Spec worktree while the check is live. Two members share one `.venv` and break each other (decision 09). If you do, a run fails at random with a broken environment.

The site evidence runner does not use `uv run`, so it runs at the same time. A pipeline test that needs `uv run` has two choices. Run it in a detached worktree of its own, or wait for the background run to end.

Before the push, read the result of the run.

- A green run needs no more work. The push does not wait on a run that is already green.
- A red run gets fixed before the push. Run again only the check of the failed member: `make -C apps/<app> check`. Do not run the full check again.
- Record the start time, the end time, and the last lines of the log in the evidence of AT-22.

## A site test

The instrument is the evidence runner, a Playwright project of the site. One command takes every shot of every site test of the feature.

1. Write `.scratch/<slug>/evidence/AT-<n>/steps.json` for each site test that asks for screenshots. See "The step list" below.
2. If any test uses the analyzer, start the local API first: `make -C apps/api api-evidence`. Run it in the background. It allows 600 requests a minute, so a test does not wait on the limit. It stays real, with real Sleeper data and real Claude calls.
3. Run the round from the Spec worktree: `pnpm --dir apps/site evidence <slug>`. Save the full output. It prints the build of each client, the time of each test, and the total.
4. Look at each shot. Write one or two sentences of what it shows about the Then line.
5. Stop the API when the round is done.

To take the shots of only some tests again, name them: `pnpm --dir apps/site evidence <slug> AT-3 AT-7`.

The runner builds each client one time per round and serves its export on `http://127.0.0.1:4173`. The build calls the local API at `http://localhost:8080`, never the production API. A missing path gets the `404.html` of the site, as the Worker gives it. The runner opens each page with `cpc.theme` set to `light` or `dark`, and scrolls the page to the end and back before each full-page shot.

### The step list

`steps.json` holds one object with these keys:

- `route`: the path under the site root, such as `/2026/week-08/`. It is the only key you must give.
- `steps`: an optional list. Each step has one verb. See the table below.
- `widths`: optional. The default is `[375, 768, 1280]`.
- `themes`: optional. The default is `["light", "dark"]`.
- `clients`: optional. The default is `["cpc"]`. Write `["cpc", "norcal"]` for a test of each client.

Narrow `widths`, `themes`, and `clients` only to match the Evidence line of the test. Set `clients` to both only when the Evidence line says "each client" or "both", or when the acceptance file says every test covers both clients. Otherwise leave `clients` out, so the default `cpc` holds. Each extra client doubles the shots of a test.

| Step | What it does |
| --- | --- |
| `{"click": "<selector>"}` | Taps the first element that matches. |
| `{"fill": {"selector": "<selector>", "value": "<text>"}}` | Types the text into the first field that matches. |
| `{"scroll": "<selector>"}` or `{"scroll": "end"}` | Scrolls the element into view, or scrolls to the end of the page. |
| `{"wait": "<selector>"}`, `{"wait": "url"}`, or `{"wait": <ms>}` | Waits for the element to show, for the URL to change after the last click, or for a time. |
| `{"shot": "<name>"}` | Takes a full-page shot with the name, such as `before`. |
| `{"url": true}` | Writes the URL of the page to a file. |

A selector is a Playwright selector, such as `button[aria-label="Add a team"]`, `button:has-text("Done")`, or `text=Suggested Counters`. Find each selector on the real built page.

With no `shot` step, the runner takes one shot after the last step. A step list with only `route` gives one shot for each width and theme. An unknown key or verb stops the run before the first shot. The error names the file and the step.

An analyzer test fills the passphrase sheet first: `{"fill": {"selector": "input[type=password]", "value": "localtest"}}`, then `{"click": "button[type=submit]"}`. Before a shot of a result, `wait` for text that only the result shows.

The runner writes these files beside `steps.json`:

- A shot is `<width>-<theme>.png`. A named shot is `<name>-<width>-<theme>.png`.
- The `url` step writes `url-<width>-<theme>.txt`.
- A test of more than one client puts the client first, such as `norcal-before-1280-dark.png`.

### A test that no verb covers

Use the `agent-browser` CLI for a test whose step no verb covers, such as a test with scripts off. Run `agent-browser skills get core` one time to learn its commands.

1. Build the site from the Spec worktree: `pnpm --dir apps/site build`. For an analyzer test, set `NEXT_PUBLIC_API_URL=http://localhost:8080`, or the site calls the production API.
2. Serve `apps/site/out` on `http://127.0.0.1:4173` with a server that answers a missing path with `404.html` and the status 404, as the Worker does. Run it in the background. `make -C apps/api api-evidence` allows only that origin.
3. For each width and theme that the Evidence line names:
   1. Set the viewport: `agent-browser set viewport <width> 900`.
   2. Open the page that the When line names.
   3. Set the theme. The site reads the key `cpc.theme` from local storage. Run `agent-browser eval "localStorage.setItem('cpc.theme','light')"` for light, or `setItem('cpc.theme','dark')` for dark.
   4. Run `agent-browser reload`, then `agent-browser wait 1000`.
   5. Scroll to the end and back to the top, so each section that reveals on scroll shows: `agent-browser eval "window.scrollTo(0, document.body.scrollHeight)"`, `agent-browser wait 1500`, then `agent-browser eval "window.scrollTo(0, 0)"`.
   6. Take the screenshot: `agent-browser screenshot <absolute path of .scratch/<slug>/evidence/AT-<n>>/<width>-<theme>.png --full`. Put the path before `--full`. With `--full` first, the CLI ignores the path and saves the file under `~/.agent-browser/tmp/`.
4. Write the steps you ran in `evidence/AT-<n>/steps.txt`, so a reader knows how each shot was made.
5. Stop the server and close the browser when the last such test is done.

## A pipeline test

1. Run the command of the When line in the Spec worktree, for the real week that the Given line names.
2. Save the command and its full output as `.scratch/<slug>/evidence/AT-<n>/output.txt`. Put the command on the first line, after `$ `.
3. If the Then line names `page.json` fields, save the changed fields as `.scratch/<slug>/evidence/AT-<n>/fields.diff`. Make it with `git diff -- <the page.json path>`, or with `jq` on the named fields.
4. Put back each tracked file of the week output with `git restore`. Only `publish` commits the week output (ADR 0019).

A test of both apps gets the pipeline files and the shots of its `steps.json`.

## EVIDENCE.md

Write `.scratch/<slug>/EVIDENCE.md` in this shape:

```markdown
# <Feature title>: evidence

Spec: `.scratch/<slug>/PRD.md`. Acceptance tests: `.scratch/<slug>/ACCEPTANCE.md`.
Built from: `<short sha>`, on <date>. The agent gives no Test verdict. The Judge gives one for each test in `VERDICTS.md`.
Round time: <N> min for <M> site tests.

## AT-1: <title>

App: site
Then: <the Then line, copied>
Files: `evidence/AT-1/steps.json`, `evidence/AT-1/375-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/1280-dark.png`
Observation: <what the files show, in one or two sentences>

## AT-2: <title>

App: pipeline
Then: <the Then line, copied>
Files: `evidence/AT-2/output.txt`, `evidence/AT-2/fields.diff`
Observation: <what the output shows>
```

`Round time` is the total that the runner prints, in whole minutes, and the count of tests with a `steps.json`.

A skipped test gets `Files: none` and the reason in its Observation line, such as "ticket 02 is blocked". A screenshot test that no verb covers names its reason too, such as "scripts off", and gets its shots from `agent-browser`.

**Stop rule of stage 3.** Commit `EVIDENCE.md` and `evidence/` on the Spec branch with the message `Record the evidence of <slug>`. The hook must pass. Then go to stage 4, [`judge.md`](judge.md). If a site build or a pipeline command fails, stop. Tell Brian the command and its error.
