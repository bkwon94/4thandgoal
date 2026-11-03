# The map and the decision ticket

The formats that `cpc:plan` writes. `docs/agents/issue-tracker.md` holds the paths. `GLOSSARY.md` holds the words.

## The map

`.scratch/<slug>/MAP.md`. The map is an index. Each decision lives on its decision ticket. The map gives one line for it and the path.

```markdown
# <Feature title>: map

App: site, pipeline, or both.
Spec branch: `<slug>`.

## DESTINATION

The one spec this map ends in, in one or two sentences.

## DECISIONS SO FAR

- <The gist of the decision.> `decisions/<NN>-<kind>-<slug>.md`.

## NOT YET SPECIFIED

- <The fog item, as one question.> `decisions/<NN>-<kind>-<slug>.md`.

## OUT OF SCOPE

- <The work past the destination.> <The reason.>
```

Write "None." under a heading with no item.

## The kind of a decision ticket

Choose the kind that clears the fog item at the lowest cost.

- `grill`: Brian decides it in a conversation. This is the default kind.
- `research`: a fact outside the repo decides it, such as an API, a library, or the Sleeper data.
- `prototype`: Brian must see it or run it before the decision, such as a layout or a state model.
- `spec`: the choice is small. The spec records it when `cpc:to-spec` writes the spec. It needs no session of its own.

## The decision ticket

`.scratch/<slug>/decisions/<NN>-<kind>-<slug>.md`. The slug names the question in two to five words.

```markdown
# <NN>: <The question, as a title>

Map: `.scratch/<slug>/MAP.md`.

**Kind:** grill

**Blocked by:** none, or the numbers of other decision tickets.

**Status:** open

## Question

The one choice that this ticket decides, and why the spec needs it.

## Decision

None yet.
```

When the ticket clears, set Status to `done`. Replace "None yet." with the decision, the reason, and who decided it. For a research ticket, name the notes file.
