# 01: The plugin is 4ag

Spec: `.scratch/rebrand/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-6, and AT-8.

**App:** both

**What to build:** Brian calls each skill of the repo plugin as `4ag:plan`, `4ag:implement`, and so on. The plugin manifest names `4ag`, the marketplace names `4ag-local`, and the project settings enable `4ag@4ag-local` with the relative path. Each skill calls the next skill by `4ag:`, and names the repo as `4thandgoal`. The root `CLAUDE.md` has the title `# 4thandgoal` and lists the six skills as `4ag:`. The docs under `docs/agents/` name `4ag:`. The help message of the `verdict` check names `4ag:review`, and the marker `<!-- cpc:agent -->` and its fixtures stay. The client slug `cpc` stays wherever it names the client.

**Blocked by:** none

**Status:** done

- [x] `claude plugin validate .claude/plugin` and `claude plugin validate .` pass, with the names `4ag` and `4ag-local`.
- [x] `.claude/settings.json` enables `4ag@4ag-local` and names no `cpc-local`.
- [x] `git grep -nE 'cpc:(plan|implement|review|to-spec|to-acceptance|to-tickets)' -- ':!.scratch' ':!docs/adr'` prints nothing.
- [x] `CLAUDE.md` lists all six skills as `4ag:`, under the title `# 4thandgoal`.
- [x] The marker line of the `verdict` check is unchanged, and the `verdict` tests pass.
- [x] `make check-fast` passes in `scripts/`, `apps/pipeline/`, and `apps/api/`.

## Comments

Merged into the Spec branch `rebrand` as 61444cb1, and the review fix 6cab4517, on 2026-11-11. Closes with the squash merge of the spec PR.
AT-1, AT-2, AT-3, AT-4, AT-6, and AT-8 have PASS from the Judge; the full check passed at 34477b17.
Read 7 files: CLAUDE.md, .scratch/rebrand/PRD.md, .scratch/rebrand/ACCEPTANCE.md, .scratch/rebrand/issues/01-the-plugin-is-4ag.md, .claude/plugin/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, scripts/verdict.py.
