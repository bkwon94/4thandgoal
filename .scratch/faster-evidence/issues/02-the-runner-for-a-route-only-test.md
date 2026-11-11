# 02: The runner for a route-only test

Spec: `.scratch/faster-evidence/PRD.md`. Acceptance tests AT-2, AT-3, AT-4, and AT-10.

**App:** site

**What to build:** One command, `pnpm --dir apps/site evidence <slug>`, reads each `evidence/AT-<n>/steps.json` of the feature and takes its shots. This ticket covers a `steps.json` with only `route`, for one client. The runner is a third Playwright project of the site, `evidence`, beside `rules` and `floor`. It reuses the floor's static server, which answers a missing path with `404.html`, and the floor's page opener. It takes 3 widths x 2 themes, named `<width>-<theme>.png`. Light is `setItem('cpc.theme','light')`. Before each full-page shot, it scrolls to the end and back to the top. It prints the time of each test and the total. An unknown verb or an unknown key stops the run before the first shot, with an error that names the file and the step.

**Blocked by:** none

**Status:** done

- [x] A test on a small real folder proves the six file names of a route-only `steps.json`.
- [x] The same test proves the light shot is light and the dark shot is dark.
- [x] The same test proves a section that reveals on scroll shows in the full-page shot.
- [x] The same test proves a missing path shows the folder's `404.html`.
- [x] A test proves a bad verb and a bad key each stop the run with the file and the step named, and no PNG written.
- [x] A real run on the week 8 page of CPC prints the time of the test and the total.
- [x] `pnpm check:fast` of the site passes.

## Comments
- Closed by the merge of PR #12.
