# The front door is the home page, and the passphrase leaves the chat

Kind: quick-win
Status: in-progress
Branch: `win-front-door-home`.
Source: the session of 2026-11-13.
Boundary: holds. 3 items of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The front door is the home page of both clients

Done condition: `clients/cpc/client.toml` and `clients/norcal/client.toml` set `front_door = true`, and the comments of `apps/site/src/app/page.tsx` and both `client.toml` files describe the front door at `/` with no hidden `/ask/` route, and the site tests of the repo clients expect the front door on.
Method: tdd
Red: at `1e578394` with `apps/site/scripts/client-build.test.mjs` of `ffda338d`, `pnpm exec vitest run scripts/client-build.test.mjs -t "has the front door on in each client of the repo"` in `apps/site`

```text
 × has the front door on in each client of the repo, with no /ask/ route
AssertionError: cpc: expected '# The values of the CPC client: the p…' to contain 'front_door = true'
+ front_door = false
 Tests  1 failed | 47 skipped (48)
```

Green: at `ffda338d`, `pnpm exec vitest run scripts/client-build.test.mjs -t "has the front door on in each client of the repo"` in `apps/site`

```text
 ✓ has the front door on in each client of the repo, with no /ask/ route
 Tests  1 passed | 47 skipped (48)
```

Test verdict: pending

### 2. The old /ask/ address sends the visitor to /

Done condition: with `front_door = true`, the client build writes a `_redirects` rule into the export that sends `/ask` and `/ask/` to `/` with a 301, and the export check fails when the rule is missing.
Method: tdd
Red: at `59fc027c` with `apps/site/scripts/client-build.test.mjs` of `2614875c`, `pnpm exec vitest run scripts/client-build.test.mjs -t "writes a _redirects rule"` in `apps/site`

```text
 × writes a _redirects rule that sends /ask and /ask/ to / with the front door on, and none with it off
Error: ENOENT: no such file or directory, open '.../apps/site/public/_redirects'
 Tests  1 failed | 48 skipped (49)
```

Green: at `2614875c`, `pnpm exec vitest run scripts/client-build.test.mjs -t "writes a _redirects rule"` in `apps/site`

```text
 Tests  1 passed | 48 skipped (49)
```

Test verdict: pending

### 3. The passphrase sits on the team sheet, not in the chat

Done condition: the team sheet asks only for the team, a chat turn that needs the API with no stored passphrase (for example none from the analyzer) first opens a passphrase modal and runs after it, the chat Thread never shows the passphrase card, and the header menu sheet holds a row to change it.
Method: tdd
Red: at `e9c941ff` with `apps/site/src/app/page-ask.test.tsx` of `72067e3b`, `pnpm exec vitest run src/app/page-ask.test.tsx -t "the passphrase modal"` in `apps/site`

```text
 × opens the modal before a question with no passphrase, never the card in the Thread, then sends the question
 × opens the modal as wrong after a 401, forgets the wrong one, and asks again after a new one
 × removes the question that waits when the manager closes the modal with Not now
 × changes the passphrase from a row of the header menu, and keeps the old one on Escape
 × marks the passphrase field of the modal as a keyboard field while it has the focus (AT-51)
AssertionError: expected <form …(2)>…(2)</form> to be null
+ Received:
<form
  aria-label="League passphrase"
TestingLibraryElementError: Unable to find role="dialog" and name "What is the league passphrase?"
TestingLibraryElementError: Unable to find an accessible element with the role "button" and name `/Change the league passphrase/`
 Tests  5 failed | 1 passed | 15 skipped (21)
```

Green: at `72067e3b`, `pnpm exec vitest run src/app/page-ask.test.tsx -t "the passphrase modal"` in `apps/site`

```text
 Tests  6 passed | 15 skipped (21)
```

Test verdict: pending

## Comments

- Item 1 was text only at the go. The flag switch failed 10 site tests that pin the repo clients to `front_door = false`, so item 1 moved to tdd.
- Item 1 also failed the 3 floor tests "covers no page title", because they opened `/`, which has no week chip on the front door. Fix `79c24cc9` opens the latest week page. Floor: cpc 153 passed, 7 skipped; norcal 149 passed.
- Brian changed the done condition of item 3 after the first build (31ea0936): no passphrase step on the team sheet; a modal opens before a chat turn that needs the API, so the weekly Topics stay open with no passphrase.
