# 07: The six-layer import test

**What to build:** A test holds the layer map as a dict of module name to layer: model, provider, load, facts, write, output. It reads the import graph of the package and the API and fails on any import from a higher layer, and names the edge. The API may import model, load, facts, and write. The test is green on `main` with no file moved. ADR 0010 records the rule.

**Blocked by:** 06

**Status:** done

- [ ] The test lists every module in the package. A new module with no layer fails the test with a message that says where to add it.
- [ ] The test reads only module names and import lines. It imports no pipeline code.
- [ ] The test is green with no folder move.

## Comments

- 2026-11-01: merged into `modular` from branch `modular-07-layer-test`, commits 8fbb696, 46b66d3, and fc8a775. 1,508 tests collected. The PRD order was wrong: the provider modules return the models, so the model layer is lowest. ADR 0010 and the PRD say so now. Five modules sit above their PRD layer with a `# PRD:` note each: history, snapshot, and season_inputs in facts; chart and live in write. Ticket 17 lowers them. The API may import every layer below output. Two reviewers passed it after one fix pass.
