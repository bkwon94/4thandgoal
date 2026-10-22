# Tone: the group chat voice for every blurb

Status: ready-for-agent
Date: 2026-10-22
Amends: the tone section of `design/specs/2026-10-20-cornerstone-weekly-design.md` and the "two jokes" rule in the tone prompt
Ships before: the week 7 build on Tuesday 2026-10-27 08:00. Week 6 gets a rewrite and a republish first.

## Problem Statement

Brian reads the week 6 page and the prose reads like a model wrote it. Every sentence has the same
shape: a claim, one number, then a wry tail clause. "Which is lucky and also the entire point of
waivers." "A branding problem for a team called To Infinity and Bijan." "Which is a lot to hang on."
The jokes land, but twelve chapters of the same shape read as a template, not as a person.

Four rules in the prompts cause this.

1. Every sentence must cite a fact, so no sentence can just react.
2. The vocabulary rule forces defined terms into the prose. "Margin driver", "the decider", and
   "recent add" repeat in every chapter.
3. "Two jokes per blurb" plus "lead with the claim" give one sentence shape: fact, then tail joke.
4. The examples in the tone prompt all share that shape, and the writer copies the examples more
   than it follows the rules.

## Solution

The voice is the league group chat. The writer is a league member who watched every game, knows
every manager, and types like a person. Short sentences. Some with no number. Contractions. A bare
reaction is allowed on its own. No chill, and the roast stays. Deadpan is one option, not the rule.

Four prompt changes and one verifier change carry it.

1. One sentence per blurb may cite no fact, if it has no digit, no team name, no player name, and
   fewer than 8 words. "Rough week." is legal. The verifier enforces the limit in code.
2. The vocabulary defines the stats for the verifier. The writer may use a plain phrase when the
   cited fact supports it: "won it" instead of "was the margin driver".
3. "Two jokes per blurb" goes away. "No filler sentence" replaces it, with a banned-pattern list.
   Three exact phrases are banned in code. The ", which" tail is capped at one per blurb in code.
4. The examples in the tone prompt are replaced by 6 to 8 sentences in the new voice, drafted from
   week 6 facts with the rewrite command, and approved by Brian.

The accuracy rules do not change. Every claim still cites a fact. The number rules do not change.

## User Stories

1. As a league member, I want the page to read like a person wrote it, so that I read every chapter instead of skimming the first.
2. As a league member, I want a sentence that just reacts, so that a bad week gets a "Rough." and not a clause.
3. As a league member, I want varied sentence shapes, so that twelve chapters do not read as one template.
4. As a league member, I want the roast to stay, so that a 1-11 team still hears about it.
5. As a league member, I want the writer to say "won it" and not "was the margin driver", so that the prose does not read like a stat sheet.
6. As a league member, I want contractions, so that the page sounds like the chat and not a column.
7. As a league member, I want no sentence that ends on "which is a lot to hang on", so that the tail joke stops.
8. As a league member, I want every number on the page to stay true, so that the humor never costs a fact.
9. As Brian, I want to approve the example sentences, so that the voice is the one I hear in my head.
10. As Brian, I want to rewrite one chapter of week 6 and compare it with the old blurb, so that I judge the voice on real facts before week 7.
11. As Brian, I want to rewrite every chapter of week 6 and republish it, so that the live page shows the new voice this week.
12. As Brian, I want the week 7 build on Tuesday to use the new voice with no manual step, so that the launchd job carries it.
13. As Brian, I want the reaction sentence capped at one per blurb, so that a blurb cannot fill its range with reactions.
14. As Brian, I want the reaction sentence to count in the sentence range, so that blurbs do not grow.
15. As the writer, I want the rules in the system prompt to say what a reaction sentence is, so that I know when to leave `fact_ids` empty.
16. As the writer, I want the vocabulary to define terms without a rule that I must use them, so that I can write the plain phrase.
17. As the writer, I want the banned patterns listed with one example each, so that I know the shape to avoid.
18. As the writer, I want examples that show the new voice, so that I copy a good shape.
19. As the verifier, I want the code check to reject a second uncited sentence, so that a cheap rule needs no Claude call.
20. As the verifier, I want the code check to reject an uncited sentence with a digit, a name, or 8 or more words, so that a claim cannot hide in a reaction.
21. As the verifier, I want the code check to reject a banned phrase the same way it rejects a banned word, so that the list lives in the vocabulary file.
22. As the verifier, I want the code check to reject a blurb with two or more ", which" tails, so that the tail joke stays rare.
23. As the Claude verifier, I want the rules to say a reaction sentence with no claim is supported, so that I do not reject "Rough week." as unsupported.
24. As the build operator, I want a failed code check to feed back to the writer on the second attempt, so that the writer fixes the shape and keeps the facts.
25. As a maintainer, I want the banned phrases and the reaction rule tested at the `write_and_verify` seam with a fake Claude, so that the tests run with no network.
26. As a maintainer, I want the prompt text asserted in tests the way rule 6 is today, so that a prompt edit that drops a rule fails loud.
27. As a maintainer, I want the glossary to define "reaction sentence", so that the term means one thing in code and in prose.

## Implementation Decisions

### The voice, in the tone prompt

- Replace the opening line. The voice is the league group chat: a member who watched every game and
  types like a person. Short sentences, varied length, contractions allowed. No chill. Roast freely.
  Deadpan allowed, not required.
- Keep the number rules as they are.
- In the humor section, remove "every blurb has at least two jokes". Add "no filler sentence": every
  sentence either states a fact or reacts to the one before it.
- Add a banned-pattern section with one example each. Patterns: the ", which is X" tail as the
  joke; the "X was not the problem, X was one of the problems" flip; "the entire point of"; "a lot
  to hang on"; "a polite way to say"; a sentence that explains the joke it just made.
- Cap: at most one sentence per blurb may end in a ", which" clause.
- Replace every example, passed and failed, with the approved set. Keep the rule that example
  numbers and names never appear in a new blurb. Keep the failed examples that teach an accuracy
  rule, rewritten in the new voice.

### The reaction sentence, in the writer prompt and the verifier

- Writer rule 1 becomes: cite one or more fact IDs for every sentence that makes a claim. One
  sentence per blurb may be a reaction with no citation. A reaction has no digit, no team name, no
  player name, and fewer than 8 words. Put it after the sentence it reacts to.
- The reaction sentence counts in the sentence range.
- The code check adds one rule set for a sentence with an empty `fact_ids` list: a digit fails, a
  scope team or player name fails, 8 or more words fails, and a second such sentence in the blurb
  fails. The failure messages name the sentence index like the other checks.
- The Claude verifier prompt adds one line: a sentence with no fact IDs and no claim is supported.
  The existing line on jokes and attitude stays.

### Vocabulary out of the prose

- Writer rule 4 becomes: when you name a stat, use its vocabulary term. You need not name the stat.
  A plain phrase that the cited fact supports is fine.
- The vocabulary file keeps every definition. The gated words stay gated: "decided", "upset",
  "recent add", "lucky", and the cause words still need their marker facts.
- Writer rule 15 keeps "lead with the claim" for a sentence that makes a claim.

### Banned phrases, in the vocabulary file and the code check

- The vocabulary file gets a "Banned phrases" section after "Banned words", one line, same format.
  Phrases: "the entire point", "one of the problems", "a lot to hang on", "a polite way to say".
- The code check reads the phrases the way it reads the banned words, and matches them as whole
  words after the names are removed.
- The code check counts sentences that contain ", which" and fails the blurb at two or more.

### The example set

- Draft 15 candidate sentences with the rewrite command on week 6, across the matchup of the week,
  the awards, two recaps, and the median chapter. Each candidate cites real week 6 facts.
- Brian keeps 6 to 8. Those go in the tone prompt as the passed examples, with the fact IDs they
  cite and one line on why each passed.
- The ticket for the examples is a stop point: it ends with a list for Brian, not with a prompt edit.

### Week 6 rewrite and republish

- After the prompts land, rewrite every chapter of week 6 with the rewrite command, one chapter
  per call, twelve calls. Read every blurb. A fallback blurb is a failed ticket.
- Brian republishes week 6. The publish command is his to run.
- The week 7 build on Tuesday runs under the new prompts with no further step.

### Glossary

- Add "reaction sentence": one sentence per blurb with no fact ID, no digit, no name, and fewer
  than 8 words, that reacts to the sentence before it.
- Add "banned phrase" next to "banned word".

## Testing Decisions

A good test gives a blurb and a chapter to the verifier and checks the failure list, or gives a
fake Claude to `write_and_verify` and checks the blurb that comes out. A test never checks how a
rule is coded.

- The code check tests live with the existing verifier tests. Prior art: the banned word test, the
  gated word test, and the sentence count test. New tests: a reaction sentence passes; a second
  reaction fails; a reaction with a digit fails; a reaction with a scope name fails; an 8-word
  reaction fails; a banned phrase fails; two ", which" tails fail and one passes.
- The prompt text tests live with the existing writer tests. Prior art: the test that rule 6 gates
  "decided" on a driver. New tests: the tone prompt has no "two jokes" line; the writer prompt
  names the reaction sentence; the vocabulary has the banned phrases line; the verifier prompt has
  the reaction line.
- The `write_and_verify` seam with a fake Claude is the highest seam. One test there: a writer that
  returns a second reaction gets feedback on the second attempt and passes with one.
- The rewrite of week 6 is a manual check, not a test. Brian judges the voice by reading.
- The seam count is one new seam, none. Every test uses a seam that exists.

## Out of Scope

- The lore file with manager nicknames and league history. Later.
- Any change to the facts, the chapters, or the sentence ranges.
- Any change to the site. The page renders the blurbs it gets.
- The rankings chapter. It is in the rankings spec and writes under these prompts once they land.
- The trade analyzer prompts. The analyzer has its own rubric and its own voice.
- A persona with a name. The voice is the chat, not a character.

## Further Notes

- The week 7 log was to be read before any prompt edit. Brian chose to ship the voice before week
  7. The week 6 rewrite is the test of the prompts on a live week.
- The verifier prompt already says a joke with no claim does not fail a sentence. The code check
  is the gap, not the Claude check.
- The rewrite command reads the saved facts and makes one Claude call per chapter. It needs no
  fetch, so a round of drafts costs twelve calls at most.
- Every Claude call runs on Brian's Mac. The GitHub Actions branch is parked.
