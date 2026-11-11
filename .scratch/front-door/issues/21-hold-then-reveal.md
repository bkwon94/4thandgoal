# 21: Hold each checked text, then reveal it

Spec: `.scratch/front-door/PRD.md`. Acceptance tests AT-8, AT-20, AT-21, AT-44. Source: H10 of `.scratch/front-door/HANDS-ON.md`.

**App:** api, site

**What to build:** No text that the manager reads is ever pulled back. The API holds the text of each Claude run of a free answer and a personal Topic until the Jev check passes, and streams the tool steps as they run. A text that passes comes whole, just before "checked", and its words sweep in from a blur on the stagger of `StreamText`. A failed text never leaves the API: the manager sees "Fixing a number…", and the rewrite runs out of sight. The site shows a text only with its "Checked" mark, so a stream in the old order shows no early word either. The data block of a personal Topic still settles first, and a kept Answer still shows whole at once.

**Blocked by:** 05, 06

**Status:** done

- [x] With a FakeJev that fails the first text, the stream holds no `text-delta` of the first text, and each text part comes after the fix part (AT-21).
- [x] A text that passes comes after "checking" and before "checked", and the tool steps come before "checking" (AT-20).
- [x] A second failed check gives the honest miss with no text part (AT-22).
- [x] On the site, no text shows before "Checked", and a failed first text never shows, for a free answer and a personal Topic.
- [x] The whole text sweeps in word by word in one read, in no more than 500 ms (AT-44).
- [x] "Checking" and "Fixing a number…" still hold for 800 ms (AT-20, AT-21), and a kept Answer still shows at once (AT-8).

## Comments
- Closes with the squash merge of the spec PR.
