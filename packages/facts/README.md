# facts: the fact tokens, the writer, the verifier, and the default voice

## Knows

- The fact tokens of `tokens.py`: the number tokens, `Nums`, and `fact`. Each fact carries every number as the page shows it.
- The writer: the prompt of each chapter, the blurb, the template blurb, and the retry of a checked Claude call.
- The verifier: the code check of each sentence against its cited facts, and the Claude check after it.
- The names: the last name of a player, the name suffixes, and the name particles.
- The chapter keys that the writer and the verifier treat apart, in `chapters.py`, such as the rankings chapter.
- The default voice, `prompts/tone.md` and `prompts/vocabulary.md`, and the rule prompts `writer.md` and `verifier.md`.
- A client `prompts/` folder overrides only `tone.md` and `vocabulary.md`. A client with no `prompts/` gets the default voice.

## Ports

- `ClaudeWriter` in `writer.py` implements the `Writer` port of `league/claude_port.py`. Every Claude call goes through `parse_call`.
- `jev_check.py` and `verifier.py` take the `Jev` port of `league/jev_port.py`. Each Jev call goes through that port.
- `load_prompt` takes `rules_dir`, so a package that owns a rule prompt, such as the analyzer rubric, reads it from its own folder.

## Does not do

- It imports no app and no core package, only `league`. `tests/test_layers.py` of the pipeline checks it.
- It builds no chapter and no fact sheet. The week and the core packages build them with the fact tokens.
- It holds no rule prompt of another package. `analysis.md`, `finder.md`, and `rubric.md` sit in `analyzer`, and `research.md` stays with the waiver board.
- It writes no published file.
