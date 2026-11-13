# Ticket 02 validation record

The clarification commit first reaches the normal check-fast hook and exits 2.
The site run reports 1,333 passing tests and one failure among 1,334 tests.
The failure is in `src/reduced-motion.test.tsx:378`:

```text
Reduced motion on the first question of the front door
fades the ask box in at the foot of the Thread, with no glide (AT-46 of front-door)
AssertionError: expected false to be true // Object.is equality
expect(boxes.some((part) => part.style.opacity === "0")).toBe(true)
```

This excerpt comes from terminal session 28388. It is not a full standalone hook log.
The next normal-hook attempt passes and creates clarification commit `84a87ae7`.
No product or test-code change occurs between these attempts.
No hook bypass or replacement assertion occurs.
The separate resumed full repository check exits zero; its complete log and metadata are retained beside this file.

The required `NODE_OPTIONS=--experimental-strip-types make check-fast BASE=readme-module-navigation` first exits 2.
The sandbox blocks the test server with `EPERM` on `listen 127.0.0.1`.
The escalated run exits zero. Both complete logs remain beside this file.
