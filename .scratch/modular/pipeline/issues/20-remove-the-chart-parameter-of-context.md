# 20: Remove the chart parameter of Context

**What to build:** `Context` in `sheet/base.py` takes `chart: ChartValues | None` and sets `self.chart`. The sheet trades module was the only reader, and ticket 19 removed it. No caller passes `chart`; `build_bundle` in `sheet/assemble.py` does not. Remove the parameter and the field. Check whether `ChartValues` still has a reader in the sheet package after that, and drop the import if not.

**Blocked by:** 19

**Status:** ready-for-agent

- [ ] `Context` has no `chart` parameter and no `chart` field.
- [ ] No unused import of `ChartValues` stays in the sheet package.
- [ ] The layer test and the full suite pass. The four golden tests pass with no golden change.

## Comments

Stays open in the audit of `todoist-queue` on 2026-11-12, as ready-for-agent. Brian kept it, because it fixes a real bug or changes what a manager sees.
Proof: `packages/week/python/src/week/sheet/base.py` still takes `chart: ChartValues | None` and sets `self.chart`, and no code reads it.
Read 1 file: .scratch/todoist-queue/audit.md.
