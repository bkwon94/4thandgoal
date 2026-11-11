# 01: The plugin is 4ag

Spec: `.scratch/rebrand/PRD.md`. Acceptance tests AT-1, AT-2, AT-3, AT-4, AT-6, and AT-8.

**App:** both

**What to build:** Brian calls each skill of the repo plugin as `4ag:plan`, `4ag:implement`, and so on. The plugin manifest names `4ag`, the marketplace names `4ag-local`, and the project settings enable `4ag@4ag-local` with the relative path. Each skill calls the next skill by `4ag:`, and names the repo as `4thandgoal`. The root `CLAUDE.md` has the title `# 4thandgoal` and lists the six skills as `4ag:`. The docs under `docs/agents/` name `4ag:`. The help message of the `verdict` check names `4ag:review`, and the marker `<!-- cpc:agent -->` and its fixtures stay. The client slug `cpc` stays wherever it names the client.

**Blocked by:** none

**Status:** ready-for-agent

- [ ] `claude plugin validate .claude/plugin` and `claude plugin validate .` pass, with the names `4ag` and `4ag-local`.
- [ ] `.claude/settings.json` enables `4ag@4ag-local` and names no `cpc-local`.
- [ ] `git grep -nE 'cpc:(plan|implement|review|to-spec|to-acceptance|to-tickets)' -- ':!.scratch' ':!docs/adr'` prints nothing.
- [ ] `CLAUDE.md` lists all six skills as `4ag:`, under the title `# 4thandgoal`.
- [ ] The marker line of the `verdict` check is unchanged, and the `verdict` tests pass.
- [ ] `make check-fast` passes in `scripts/`, `apps/pipeline/`, and `apps/api/`.
