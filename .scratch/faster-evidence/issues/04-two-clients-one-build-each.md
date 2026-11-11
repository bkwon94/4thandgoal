# 04: Two clients with one build each

Spec: `.scratch/faster-evidence/PRD.md`. Acceptance test AT-7.

**App:** site

**What to build:** A `steps.json` can name `clients`, with the default `cpc`. In one run, the runner builds each client one time, serves its export, takes the shots of every test of that client, then builds the next client. A test with more than one client puts the client first in each file name: `<client>-<width>-<theme>.png`, or `<client>-<name>-<width>-<theme>.png`. The runner makes no worktree.

**Blocked by:** 02

**Status:** done

- [x] A real run with two tests, each with `clients: ["cpc", "norcal"]`, shows one build of each client in the output.
- [x] Each file of that run starts with `cpc-` or `norcal-`, and each shot shows the brand of its client.
- [x] A test with no `clients` key gets no client prefix.
- [x] `git worktree list` is the same before and after the run.
- [x] `pnpm check:fast` of the site passes.

## Comments
- Closed by the merge of PR #12.
