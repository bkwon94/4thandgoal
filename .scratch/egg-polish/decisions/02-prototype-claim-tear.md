# 02: How does a tear of the ticket stub become the claim?

Map: `.scratch/egg-polish/MAP.md`.

**Kind:** prototype

**Blocked by:** 01

**Status:** done

## Question

The claim sheet ends with a claim button now. Tear Ticket tears a stub off along a perforation. The spec needs the moment the tear sends the claim, the state while the API answers, a path for an error, and a fallback with no WebGL. A failed claim on Tuesday blocks a manager.

## Decision

The claim is a tear of the stub of a claim ticket. Brian approved the prototype on 2026-11-08.

1. The ticket replaces the claim button at the foot of the claim sheet. It shows the letter tile, the egg word or the block, and the team.
2. Until the team, the egg word, and the passphrase are done, the stub is locked. It names the next missing step, as the button does now.
3. A drag of the stub to the right tears it. The holes of the perforation pop from the top down as the drag goes.
4. A release before a full tear springs the stub back. Nothing sends.
5. A tap on the stub with no drag tears it by itself. Enter or Space on the stub does the same, so the tear needs no gesture.
6. A full tear sends the claim. The stub flutters away, and the ticket shows a sweep while the API answers.
7. A claim stamps CLAIMED on the ticket, then the end card shows as now.
8. Another manager first stamps TAKEN, and the stub joins the ticket again. A wrong passphrase shows the error, and the stub joins again, so the manager can tear again.

The parts are SVG and CSS only, with no WebGL. With reduced motion, the stub leaves and the stamp shows with no motion.
The canvas is https://claude.ai/artifact/HaTnYegqcyt1VS9eh1c1wq, board "Claim by a tear".
