# Use lines on the week parts

Kind: quick-win
Status: done
Branch: `win-week-use-lines`.
Source: the handoff file `.handoff/2026-11-21-quick-test-fixes.md`, item 2.
Boundary: holds. 1 item of one kind; no new term or ADR; no moved seam; each done condition is one sentence.

## Items

### 1. The week parts have no use lines

Done condition: The top docstrings of `packages/week/site/parts/share-bar.tsx` and `packages/week/site/parts/week-chapter.tsx` each hold a "Use it when:" line and a "Do not use it when:" line, in the style of `packages/design/site/parts/*.tsx`.
Method: text only
Red: none, text only.
Green: at `58e9a831`, the diff of the text: two lines in the top docstring of each file, `share-bar.tsx` and `week-chapter.tsx`.
Test verdict: none

## Smoke

Smoke: none, no site or API change.

## Comments

Closes with the squash merge of the PR of `win-week-use-lines`. Commits: `afbc2a60`, `58e9a831`. Date: 2026-11-21.
The item is text only, so it has no loop; `make check-fast BASE=main` passed with 1955 tests and 0 failed.
The rule `design/use-lines` still checks only `packages/design/site/`; a later run can widen it to `packages/*/site/parts/` if Brian asks.
Read 7 files: .handoff/2026-11-21-quick-test-fixes.md, packages/week/site/parts/share-bar.tsx, packages/week/site/parts/week-chapter.tsx, packages/design/site/parts/card.tsx, packages/design/site/parts/chapter.tsx, packages/design/site/parts/bar-fill.tsx, packages/design/lint/rules/use-lines.mjs.
