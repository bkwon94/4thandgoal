---
name: to-spec
description: Write the spec of one feature of this repo as .scratch/<feature>/PRD.md, in our header format, from the map, the decision tickets, and the conversation. Use after 4ag:plan clears the fog, or when Brian asks for a spec of a feature with no fog.
argument-hint: '<feature slug>'
---

# To spec

Write the spec of one feature as `.scratch/<slug>/PRD.md`. Do not interview Brian. Use what the map, the decision tickets, and this conversation already hold.

## Before you start

1. Check that the skill `to-spec` is in the available skill list. If it is missing, stop. Tell Brian its name. Do not guess its steps.
2. Find the feature slug. If `.scratch/<slug>/MAP.md` exists, read it and every file in `decisions/`.
3. If a decision ticket other than a `spec` ticket is still open, stop. Tell Brian to run `4ag:plan <slug>` first.

## Steps

1. Call the Skill tool for `to-spec`. Do its steps 1 to 3, with the changes below.
2. Its step 2 asks Brian to check the test seams. Do not stop for it. Name the seams under Testing Decisions, and Brian checks them with the spec.
3. Use the words of `GLOSSARY.md`. Respect the ADRs in `docs/adr/` of the area that the spec changes.
4. Record the choice of each open `spec` decision ticket under Implementation Decisions.
5. Write the file to `.scratch/<slug>/PRD.md`, not to another tracker. Add no triage label.
6. Start the file with the header below, then the sections of the `to-spec` template, as `##` headings in its order.
7. Show Brian the spec. Do not change it after Brian approves it, except to fix what Brian asks for.

## The header

Copy this shape from `.scratch/one/PRD.md`:

```markdown
# <Feature title>

Status: ready-for-agent
Date: <today, YYYY-MM-DD>
Apps: site, pipeline, or both. Name what each app does.
Spec branch: `<slug>`.
Source: the map `.scratch/<slug>/MAP.md` and decision tickets <NN> to <NN>, or the session of <date>. ADRs, if any.
Tickets: none yet. `4ag:to-tickets` writes them.
```

The Spec branch is the feature slug. A ticket branch of the spec is `<slug>-<NN>` (ADR 0019).

## The end

Tell Brian that `4ag:to-acceptance <slug>` is next.
