# 12: Where the Judge writes its verdicts and how the check reads them

Map: `.scratch/fast-cycle/MAP.md`.

**Kind:** spec

**Blocked by:** 06, 08

**Status:** done

## Question

The spec must set the file and the format of the Judge's verdicts, how `scripts/verdict.py` reads them and a FAIL from Brian, and what changes in `cpc:implement`, `cpc:review`, and `verdict.yml`. The orchestrator must not be able to edit a verdict of the Judge without a trace.

## Decision

The spec decided it on 2026-11-06. See "The Judge (decisions 06, 07, 08, and 12)" and "The check `verdict` (decision 12)" under Implementation Decisions of `.scratch/fast-cycle/PRD.md`.
