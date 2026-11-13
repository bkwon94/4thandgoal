# Infrastructure startup probes

Implementation revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
The archive holds exactly two infrastructure-only startup probes and zero cold task trials.
Each probe receives only `Reply OK.`; neither receives any approved task prompt.
Both commands exit before agent startup with the same in-process app-server permission error.
Both stdout files contain zero bytes. Neither trace directory exists.
The manifest preserves each exact command, reported exit code, output size, and output hash.
The orchestrator supplies commands and exit statuses; this worker verifies the archived output bytes.

Probe 2 uses supported sqlite_home and log_dir CLI overrides under /tmp.
The orchestrator reports that SQLite files appear under the selected /tmp directory before the same startup error.
No source config, HOME, CODEX_HOME, auth, instructions, or sandbox setting changes.
Neither probe establishes an automatic context inventory or any task result.
No cold task agent starts; no task failure, chosen paths, reasons, or file counts are inferred.

Fresh collaboration agents start at the main checkout, per the orchestrator’s launch observation.
This directory has no independent trace of that collaboration-agent observation.
That start directory cannot prove the fixed spec-root procedure.

## Probe 1

```sh
CODEX_ROLLOUT_TRACE_ROOT=/tmp/readme-context-probe codex exec --ephemeral --json -C /Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation -m gpt-6-astra 'Reply OK.' > /tmp/readme-context-probe.stdout.jsonl 2> /tmp/readme-context-probe.stderr
```

## Probe 2

```sh
mkdir -p /tmp/readme-context-probe2-db /tmp/readme-context-probe2-logs; CODEX_ROLLOUT_TRACE_ROOT=/tmp/readme-context-probe2 codex exec --strict-config -c 'sqlite_home="/tmp/readme-context-probe2-db"' -c 'log_dir="/tmp/readme-context-probe2-logs"' --ephemeral --json -C /Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation -m gpt-6-astra 'Reply OK.' > /tmp/readme-context-probe2.stdout.jsonl 2> /tmp/readme-context-probe2.stderr
```

## Full repository check

Command: `NODE_OPTIONS=--experimental-strip-types make check`.
Working directory: `/Users/brian.kwon/repos/4thandgoal/.claude/worktrees/readme-module-navigation`.
Checkout HEAD: `85d54d463a6bb111bb37c58bd810c24d1d9f4131`. Product revision: `dad744db4f3b49732adc1586e08c34be2f381f73`.
Start: `2026-11-12T20:54:16.841501+00:00`. End: `2026-11-12T20:56:41.866026+00:00`. Exit code: `2`.
The full output and metadata appear in `readme-full-check.log` and `readme-full-check.meta.json`.
The log reports 131 site unit-test files and 1,334 tests passed before the browser rule suites.
Chromium startup fails at `bootstrap_check_in org.chromium.Chromium.MachPortRendezvousServer` with `Permission denied (1100)`.
Playwright reports 22 rule tests failed and one passed; the site check then stops.
The site build and export steps do not run after the browser failure.
The later pipeline and API members do not run in this full-check invocation.
The full repository check remains incomplete. This record gives no acceptance Test verdict.
No product behavior, test behavior, or sandbox restriction changes to bypass this failure.
The two independent startup probes remain non-task probes; the cold-trial count remains zero.
