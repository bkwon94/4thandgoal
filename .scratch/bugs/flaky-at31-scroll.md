# AT-31 of the home page test fails often in the commit hook

Kind: bug
Status: done
Branch: `bug-flaky-at31-scroll`.
Source: the session of 2026-11-16.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. AT-31 in `apps/site/src/app/page.test.tsx` fails often in the commit hook

Done condition: AT-31 in `apps/site/src/app/page.test.tsx` passes in each of 20 runs of the full site unit suite, the load that the commit hook puts on it.
Method: diagnosing-bugs
Cause: AT-31 in `apps/site/src/app/page.test.tsx` reads its record of `scrollIntoView` right after `openTopic` returns, but the scroll effect in `apps/site/src/app/front-door/front-door.tsx` asks for the scroll in `frame.postRender` of the next motion frame, so under load the test clears the record before the scroll of Week recap lands, or reads it before the scroll of Power rankings lands.
Red: at `a85360e7`, run at the worktree root with Node 24 first on PATH. The loop runs 20 full site unit suites, 4 at a time in 5 rounds, the load of hooks in several worktrees at once.

```sh
bash -c 'cd apps/site && L=$(mktemp -d) && CLIENT=cpc node scripts/client-build.mjs >/dev/null && for r in 1 2 3 4 5; do for c in 1 2 3 4; do pnpm test > "$L/$r-$c.log" 2>&1 & done; wait; done; if grep -l "FAIL .*(AT-31)" "$L"/*.log; then grep -h -A9 "FAIL .*(AT-31)" "$L"/*.log; exit 1; fi; grep -h "Tests " "$L"/*.log | sort | uniq -c; echo "AT-31 passed in each of 20 runs"'
```

```text
/var/folders/.../tmp.TptX1zMxvt/1-4.log
/var/folders/.../tmp.TptX1zMxvt/5-2.log
 FAIL  src/app/page.test.tsx > the Thread of Lil Fridge > scrolls each new question to its top under the Thread header, and leaves the older Answers in place (AT-31)
AssertionError: expected <article …(2)>…(2)</article> to be <article …(2)>…(2)</article> // Object.is equality
-   aria-label="Power rankings"
+   aria-label="Week recap"
--
 FAIL  src/app/page.test.tsx > the Thread of Lil Fridge > scrolls each new question to its top under the Thread header, and leaves the older Answers in place (AT-31)
AssertionError: expected [ <article …(2)>…(2)</article>, …(1) ] to not include <article …(2)>…(2)</article>
 ❯ src/app/page.test.tsx:377:26
    377|     expect(scrolled).not.toContain(recap);
exit 1
```

Green: at `6151eb9f`, the same command.

```sh
bash -c 'cd apps/site && L=$(mktemp -d) && CLIENT=cpc node scripts/client-build.mjs >/dev/null && for r in 1 2 3 4 5; do for c in 1 2 3 4; do pnpm test > "$L/$r-$c.log" 2>&1 & done; wait; done; if grep -l "FAIL .*(AT-31)" "$L"/*.log; then grep -h -A9 "FAIL .*(AT-31)" "$L"/*.log; exit 1; fi; grep -h "Tests " "$L"/*.log | sort | uniq -c; echo "AT-31 passed in each of 20 runs"'
```

```text
  20       Tests  1525 passed (1525)
AT-31 passed in each of 20 runs
exit 0
```
Test verdict: PASS

## Comments

Closes with the squash merge of the PR of `bug-flaky-at31-scroll`. Commits: `a85360e7`, `6151eb9f`, `800fd833`, `bc32ad43`, `c1cc1ec6`. Date: 2026-11-16.
The site suite has 1525 tests, all pass, and the loop of item 1 went red in 2 of 20 runs at `a85360e7`, then green in 20 of 20 at `6151eb9f`.
AT-31 failed only when 4 suites ran at the same time, so a later flaky test of the Thread can use the same 4-at-a-time loop.
Read 10 files: AGENTS.md, apps/site/AGENTS.md, GLOSSARY.md, docs/agents/issue-tracker.md, docs/adr/0033-a-quick-run-skips-the-spec-flow.md, .claude/plugin/skills/quick/format.md, .claude/plugin/skills/quick/judge.md, .claude/plugin/skills/implement/build.md, apps/site/src/app/page.test.tsx, apps/site/src/app/front-door/front-door.tsx.
