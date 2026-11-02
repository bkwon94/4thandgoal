# Agent habits: the tracker measures the vision, and a cold agent starts from the tracker

Status: ready-for-agent
Date: 2026-11-02
Repos: the pipeline `cornerstone-fantasy-sleeper-weekly-report` and the site `cpcfantasyfootball`. The same PRD sits in both.
Source: One's `~/repos/zero/docs/VISION.md` and `~/repos/zero/docs/adr/0014-a-merge-request-merges-on-the-verdicts-of-its-acceptance-tests.md`.
Tickets: 01 and 02 in both repos. 03 in the pipeline only.

## Problem Statement

The north star of One: "An agent must be able to change any product in this repository without reading most of
it." The test: an agent that has never seen the repo makes the change after it reads at most 100k tokens.

Three habits serve that test, and no ticket holds them yet. Brian agreed each matters. Each is a proposal.
Brian decides before an agent builds one.

1. No close comment says how much the agent read. We cannot tell if the vision holds, or which folder costs most.
2. A cold agent starts from a handoff file that one session wrote for the next. The tracker is the record, and
   the handoff is a copy that drifts.
3. The API on Fly deploys by hand from a shell. No check gates it, and no record says when it ran.

## Solution

1. **A close comment lists the files the agent read** (ticket 01). The list is the measure of the vision. A
   folder that every ticket reads is the next README or the next split.
2. **A state file lists each open feature and its next step** (ticket 02). `docs/agents/state.md`. A cold agent
   reads the tracker and not a handoff. A rule test keeps it true.
3. **A deploy step for the Fly API behind the check and an approval** (ticket 03, pipeline only). CI deploys from
   `main` after the check passes and Brian approves. An ADR records the decision.

## Decisions

- **Each habit is a proposal.** The status of each ticket is needs-triage until Brian says build it.
- **The list of files read is the agent's claim**, not evidence. One 0014 draws that line. The list still pays:
  an agent that must list what it read reads less.
- **The state file is a list, not a log.** One line per open feature. The close comment of a ticket updates it.
- **A deploy is a human decision.** The check gates it, and Brian approves it. No deploy runs on a push alone.

## Out of Scope

- A token count. No tool here counts the tokens an agent read, and a file count is enough to see the trend.
- A deploy of the site. The site publishes through `cornerstone publish`, and that stays.
- A handoff file. Once the state file exists, a session writes no handoff.
