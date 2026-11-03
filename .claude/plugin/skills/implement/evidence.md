# The evidence

Stage 3 of `cpc:implement`. Record the evidence of each acceptance test `AT-<n>` of `.scratch/<slug>/ACCEPTANCE.md`. The evidence uses real data and a real build, with no mock (ADR 0020).

The evidence states what the instrument showed. It holds no PASS, no FAIL, and no BLOCKED. Only Brian gives a Test verdict.

## Before the first test

1. Start after the last commit of stage 2, so that each file shows the head commit. Write down `git rev-parse --short HEAD`.
2. Skip a test whose ticket is `blocked`, or is behind a `blocked` ticket. Its entry in `EVIDENCE.md` names the ticket.
3. Skip a test with the word `Retired` in its title.

## A site test

The instrument is the `agent-browser` CLI. Run `agent-browser skills get core` one time to learn its commands.

1. Build the site from the Spec worktree: `pnpm --dir apps/site build`.
2. Serve the export: `python3 -m http.server 4173 --directory apps/site/out`. Run it in the background.
3. For each width of 375, 768, and 1280 px, and each theme of light and dark:
   1. Set the viewport: `agent-browser set viewport <width> 900`.
   2. Open the page that the When line names, under `http://localhost:4173/`.
   3. Set the theme. The site reads the key `cpc.theme` from local storage. Run `agent-browser eval "localStorage.setItem('cpc.theme','dark')"` for dark, or `removeItem('cpc.theme')` for light. Then reload the page.
   4. Take the screenshot: `agent-browser screenshot --full .scratch/<slug>/evidence/AT-<n>/<width>-<theme>.png`.
4. Look at each screenshot. Write one or two sentences of what it shows about the Then line.
5. Stop the server and close the browser when the last site test is done.

Each site test gets six files: `375-light.png`, `375-dark.png`, `768-light.png`, `768-dark.png`, `1280-light.png`, and `1280-dark.png`.

## A pipeline test

1. Run the command of the When line in the Spec worktree, for the real week that the Given line names.
2. Save the command and its full output as `.scratch/<slug>/evidence/AT-<n>/output.txt`. Put the command on the first line, after `$ `.
3. If the Then line names `page.json` fields, save the changed fields as `.scratch/<slug>/evidence/AT-<n>/fields.diff`. Make it with `git diff -- <the page.json path>`, or with `jq` on the named fields.
4. Put back each tracked file of the week output with `git restore`. Only `publish` commits the week output (ADR 0019).

A test of both apps gets the pipeline files and the six screenshots.

## EVIDENCE.md

Write `.scratch/<slug>/EVIDENCE.md` in this shape:

```markdown
# <Feature title>: evidence

Spec: `.scratch/<slug>/PRD.md`. Acceptance tests: `.scratch/<slug>/ACCEPTANCE.md`.
Built from: `<short sha>`, on <date>. The agent gives no Test verdict. Brian gives one for each test.

## AT-1: <title>

App: site
Then: <the Then line, copied>
Files: `evidence/AT-1/375-light.png`, `evidence/AT-1/375-dark.png`, `evidence/AT-1/768-light.png`, `evidence/AT-1/768-dark.png`, `evidence/AT-1/1280-light.png`, `evidence/AT-1/1280-dark.png`
Observation: <what the files show, in one or two sentences>

## AT-2: <title>

App: pipeline
Then: <the Then line, copied>
Files: `evidence/AT-2/output.txt`, `evidence/AT-2/fields.diff`
Observation: <what the output shows>
```

A skipped test gets `Files: none` and the reason in its Observation line, such as "ticket 02 is blocked".

**Stop rule of stage 3.** Commit `EVIDENCE.md` and `evidence/` on the Spec branch with the message `Record the evidence of <slug>`. The hook must pass. If a site build or a pipeline command fails, stop. Tell Brian the command and its error.
