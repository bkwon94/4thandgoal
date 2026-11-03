# 03: Roast as the default register

Spec: `.scratch/next-week-byes/pipeline/PRD.md`, "The tone prompt". Follows `.scratch/tone/PRD.md`.

**What to build:** The tone prompt stops counting jokes. Its Humor section is voice guidance: roast is the
default register of the group chat, wherever a fact invites it, early or late, as often as the facts
allow. The banned patterns, the reaction sentence rules, and the number rules stay.

**Blocked by:** None (can start immediately).

**Status:** done

- [x] "Every blurb has at least one joke" and "Roast bad teams harder" leave the rules. Their meaning returns as guidance, not as a count.
- [x] The guidance names the invitations: a record below .500, a bench with no cover, a benched star, a team name that writes its own joke.
- [x] The banned patterns section does not change. The verifier does not change.
- [ ] Every prompt test and the writer tests pass. `uv run pytest -q` and `uv run ruff check src tests` pass.
- [ ] The read of the week 7 build in ticket 05 is the test of the voice.

## Comments

- 2026-11-02: `main` holds the merge 9d9ecc8. Status set to done by the state-file sweep of agent-habits 02.
