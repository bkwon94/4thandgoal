# 03: How does the cold agent test count files?

Map: `.scratch/readme-module-navigation/MAP.md`.

**Kind:** grill

**Blocked by:** 01, 02

**Status:** done

## Question

Which test procedure proves that a cold agent finds the correct module and test within the inclusive 10-file limit?
Brian chooses the allowed starting context, search rules, file count rules, and number of trials per task.
The count includes instructions and READMEs; each agent records every file read.
Resolve how partial reads, search results, repeated reads, and files outside the repo count toward the limit.
Define what makes an agent cold and how the test withholds expected answers.
The evidence must show each agent's path choices, reasons, and complete read record.
The procedure supplies evidence; the Judge gives each acceptance test its Test verdict.

## Decision

Brian approves the procedure below for the six tasks from decision 01.

### Cold start and tracker exception

Each task has one fresh agent at the repository root, with no inherited history or expected answers.
Each agent receives only its approved behavior prompt and the common test procedure.
Repository and external instructions still apply, except for the test-only exception below.

The test-only exception suspends the normal state and ticket reads for these trials.
Cold agents cannot read `.scratch/` or `docs/agents/state.md`, because the tracker holds the expected answers.
This exception applies only to the cold-agent trials. Normal work keeps the state and ticket rules from decision 02.
All other instruction and README reads count toward the ten-file limit.

### Trials and success conditions

Run one fresh agent per approved task, for six runs in total.
All six runs use the same model and repository revision.
Each run must name the correct target module and relevant test file within ten distinct file reads.
Each agent gives reasons for both choices and an ordered, complete file-read log.
All six runs must meet these conditions. Keep failed runs as evidence.
The procedure records evidence. The Judge supplies each acceptance test's Test verdict.

### File count and audit

Each distinct file counts once, including partial reads, READMEs, and automatically loaded instruction files.
Files outside the repository count too, including external instruction files.
Repeated reads of the same file add no further count.
Every file that content search exposes counts toward the limit.
Filename listings expose names only and cost no file reads.
The eleventh distinct file fails the run.

The auditor compares each agent's ordered read log with the complete tool trace.
The audit also uses the automatic context inventory to account for instruction files that load without a tool call.
The evidence includes each agent's path choices, reasons, complete read log, and the audit record.

Brian approves this procedure and its test-only exception to the state and ticket rules from decision 02.
This decision defines the trials. It does not run them or change product documentation or code.

## Clarification, 2026-11-12

Brian excludes automatic skill catalog metadata from the ten-file count.
Actual file reads and loaded instructions still count.
All other trial conditions remain unchanged.
