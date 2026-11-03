# 20: Remove the chart parameter of Context

**What to build:** `Context` in `sheet/base.py` takes `chart: ChartValues | None` and sets `self.chart`. The sheet trades module was the only reader, and ticket 19 removed it. No caller passes `chart`; `build_bundle` in `sheet/assemble.py` does not. Remove the parameter and the field. Check whether `ChartValues` still has a reader in the sheet package after that, and drop the import if not.

**Blocked by:** 19

**Status:** ready-for-agent

- [ ] `Context` has no `chart` parameter and no `chart` field.
- [ ] No unused import of `ChartValues` stays in the sheet package.
- [ ] The layer test and the full suite pass. The four golden tests pass with no golden change.
