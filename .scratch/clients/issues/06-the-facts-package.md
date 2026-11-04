# 06: The facts package

Spec: `.scratch/clients/PRD.md`. Acceptance tests AT-1.

**App:** pipeline

**What to build:** The fact tokens, the writer, the verifier, and the names move into the `facts` package. Each rule prompt moves into the package that owns it, and the default voice lives in `facts`.

**Blocked by:** 05

**Status:** in-review

- [x] The `facts` package holds the modules of decision 01.
- [x] The `writer` and `verifier` prompts move into `facts`. The other rule prompts wait in place for the ticket of their package.
- [x] `tone.md` and `vocabulary.md` are the default voice in `facts`. The client `prompts/` folder overrides only those two files, and CPC keeps its voice.
- [x] A client with no `prompts/` folder builds with the default voice.
- [x] The CPC golden diff is empty (AT-1).
