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
Red: pending
Green: pending
Test verdict: pending

### 3. The passphrase sits on the team sheet, not in the chat

Done condition: on a first visit with no stored passphrase, the team sheet asks for the team and then the passphrase, the chat Thread never shows the passphrase card, a passphrase already stored (for example from the analyzer) skips that step, and the header menu sheet holds a row to change it.
Method: tdd
Red: pending
Green: pending
Test verdict: pending

## Comments

- Item 1 was text only at the go. The flag switch failed 10 site tests that pin the repo clients to `front_door = false`, so item 1 moved to tdd.
