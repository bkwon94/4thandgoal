# 11: Every chapter is `facts(bundle, config)`

**What to build:** Each chapter module exports one function, `facts(bundle, config)`, that returns the list of facts for that chapter. The assembly calls each in order and joins the lists. A chapter function reads no file, no environment variable, and no global. The league facts module and the trade facts module move under the sheet as chapters of the same shape.

**Blocked by:** 03, 10

**Status:** ready-for-agent

- [ ] Every chapter module has one public `facts` function with the same signature.
- [ ] The assembly is a list of chapter functions in order, and nothing else decides the order.
- [ ] A test calls one chapter with the fixture bundle and a config and gets its facts.
- [ ] The four golden tests pass with no golden change.
