# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`GLOSSARY.md`** at the repo root. It holds the terms of the site and the pipeline, one section per app.
- **`docs/adr/`** at the repo root. It holds one ADR series for both apps. Read the ADRs that touch the area you're about to work in.
- **`docs/adr/README.md`** maps each old app number to its new number. An old ticket or commit may cite an old number.

The pipeline has no glossary and no ADR folder of its own.

## File structure

```
/
├── GLOSSARY.md
├── docs/adr/
│   ├── README.md
│   ├── 0001-read-the-trade-value-chart-from-its-image.md
│   └── 0002-grade-from-known-games-not-the-last-completed-week.md
└── apps/
    ├── pipeline/
    └── site/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `GLOSSARY.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/grill-with-docs`).

## Flag ADR conflicts

If your output contradicts an existing ADR, surface it explicitly rather than silently overriding:

> _Contradicts ADR 0010 (six layers import downward only) — but worth reopening because…_
