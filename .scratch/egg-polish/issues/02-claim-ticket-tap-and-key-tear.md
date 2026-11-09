# 02: The claim ticket, torn by a tap or a key

Spec: `.scratch/egg-polish/PRD.md`. Acceptance tests AT-9, AT-10, and AT-13 to AT-19.

**App:** site

**What to build:** The claim ticket replaces the claim button at the foot of the claim sheet. It shows the letter tile, the egg word or the block, and the team. Until the team, the egg word, and the passphrase are done, the stub is locked and names the next missing step. A tap on the stub, or Enter or Space, tears it and sends the claim. A claim stamps CLAIMED and then shows the end card. Another manager first stamps TAKEN, brings the stub back, and shows that end card. A wrong passphrase shows its error and brings the stub back. Reduced motion shows each change with no motion. `GLOSSARY.md` already holds the term Claim ticket.

**Blocked by:** None. It can start now.

**Status:** in-review

- [x] A hunt test reads the ticket with the letter, the egg word, and the team after the three steps.
- [x] A hunt test taps a locked stub, reads the next missing step on it, and reads that the port got no claim.
- [x] A hunt test taps the stub and reads one claim through the port, then the CLAIMED stamp, then the end card.
- [x] A hunt test presses Enter, and another presses Space, and each reads one claim. The accessible name of the stub names the letter and the word.
- [x] A hunt test reads TAKEN and the stub back when the port answers that another manager was first.
- [x] A hunt test reads the error of a wrong passphrase and the stub back, then a second tear that claims.
- [x] A hunt test reads the block on the ticket when the letter fits no egg word of the manager.
- [x] The hunt test with motion off reads the stamp with no motion.
