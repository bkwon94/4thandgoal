# 02: Banned phrases and the ", which" cap

**What to build:** Four exact phrases fail the code check: "the entire point", "one of the problems", "a lot to hang on", "a polite way to say". They live in a "Banned phrases" line in the vocabulary file, after "Banned words", in the same format, and the code check reads them the same way. A blurb with two or more sentences that contain ", which" fails the code check. The tone prompt gets a banned-pattern section with one example each: the ", which is X" tail as the joke, the "not the problem, one of the problems" flip, the three phrases, and a sentence that explains its own joke. The glossary defines "banned phrase".

Spec: `.scratch/tone/PRD.md`, section "Banned phrases".

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] The vocabulary file has a "Banned phrases" section with the four phrases on one line.
- [ ] The code check fails a sentence with a banned phrase, matched as whole words after the names are removed, with the phrase in the message.
- [ ] The code check fails a blurb with two ", which" sentences and passes one.
- [ ] The tone prompt has the banned-pattern section with one example per pattern, and the cap of one ", which" tail per blurb.
- [ ] Prompt text tests guard the banned phrases line and the banned-pattern section.
- [ ] Code check tests cover a banned phrase, two tails, and one tail.
- [ ] The glossary defines "banned phrase" next to "banned word".
- [ ] `make test` passes. Lint count on the branch is no higher than on main.

## Comments

- 2026-10-22: built on `tone` at `8d3b94d`, two Opus reviews, one fix pass. Awaits Brian merge with `--no-ff`.
