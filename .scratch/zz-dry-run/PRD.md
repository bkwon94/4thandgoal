# Bye week on the manager page

Status: ready-for-agent
Date: 2026-11-03
Apps: both. The pipeline adds the bye week of each listed player to `managers.json`. The site shows it in each top performer row and each best add row.
Spec branch: `zz-dry-run`.
Source: the map `.scratch/zz-dry-run/MAP.md` and decision tickets 01 to 02. ADR 0006, ADR 0011. (dry run)
Tickets: 01 to 02, in `issues/`.

## Problem Statement

A manager reads his top performers and his best adds, but he cannot see when each player sits out. He must look up each NFL team bye on another site. (dry run)

## Solution

Each top performer row and each best add row on the manager page shows the NFL bye week of the player's team. A bye that has passed shows as passed. (dry run)

## User Stories

1. As a manager, I want each top performer row to show the bye week, so that I know when my best players sit out.
2. As a manager, I want each best add row to show the bye week, so that I know if an add covers a bye.
3. As a manager, I want a passed bye to read as passed, so that I do not plan around it.
4. As a manager, I want a player who changed NFL teams to show the bye of his team now, so that the week is true.
5. As a reader on a phone, I want the bye week to fit in the row at 375 px, so that the row does not wrap.
6. As a reader in the dark theme, I want the bye text to keep its contrast, so that I can read it.

## Implementation Decisions

- The pipeline owns the bye week (ADR 0011). It adds a `bye_week` number to each top performer and each best add of each manager in `managers.json`. The number is null when the schedule has no bye for the team.
- The schedule source is the NFL schedule that the bye line of the next-week cards already reads.
- The site schema of `managers.json` gets the optional field. A row with a null bye shows no bye text.
- **The text (decision 02, kind spec).** A bye still to come reads "Bye 9". A bye that has passed reads "Bye done". (dry run)
- The page gets no roster list (decision 01).

## Testing Decisions

- A good test checks what a reader sees or what the published file holds, not how the code builds it.
- The pipeline test reads a real week, `2026` week 8, and checks the `bye_week` fields in `managers.json`. Prior art: the tests of the manager entry in the pipeline.
- The site test renders the manager page from the week 8 `managers.json`. Prior art: the manager page tests of the site.

## Out of Scope

- The bye line of the next-week game cards.
- A roster list on the manager page.

## Further Notes

None. (dry run)
