# 07: The six-layer import test

**What to build:** A test holds the layer map as a dict of module name to layer: provider, model, load, facts, write, output. It reads the import graph of the package and the API and fails on any import from a higher layer, and names the edge. The API may import model, load, facts, and write. The test is green on `main` with no file moved. ADR 0007 records the rule.

**Blocked by:** 06

**Status:** ready-for-agent

- [ ] The test lists every module in the package. A new module with no layer fails the test with a message that says where to add it.
- [ ] The test reads only module names and import lines. It imports no pipeline code.
- [ ] The test is green with no folder move.
