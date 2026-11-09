# 03: The drag tear

Spec: `.scratch/egg-polish/PRD.md`. Acceptance tests AT-11 and AT-12.

**App:** site

**What to build:** A manager drags the stub of the claim ticket to the right. The holes of the perforation pop from the top down as the drag goes. A full tear flutters the stub away, shows the sweep, and sends the claim. A release before a full tear springs the stub back and sends nothing. A vertical move on the stub does not tear it.

**Blocked by:** 02

**Status:** ready-for-agent

- [x] A hunt test fires a pointer drag to the full length and reads one claim through the port.
- [x] A hunt test fires a drag to half the length, releases, and reads no claim and the stub back on the ticket.
- [x] A hunt test reads more popped holes at a longer drag, from the top hole down.
- [x] A pointer cancel during a drag springs the stub back and sends nothing.
