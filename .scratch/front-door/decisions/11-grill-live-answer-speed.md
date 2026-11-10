# 11: How does a live personal Answer stay fast and cheap?

Map: `.scratch/front-door/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** open

## Question

The personal Topics are live (decision 01). One Claude answer takes about 20 to 27 s and costs about $0.04 to $0.10 (`03-research-jev-live-cost.notes.md`). Decide if the API keeps a personal Answer until the roster changes. Decide if a Suggestion builds its Answer before the tap. Decide what the manager sees during the wait. Decide also how the personal Answers count against the caps of decision 04. Decide if the Answer streams, and with which parts: the Vercel AI SDK (`useChat`) on the site, and Pydantic AI or the plain `anthropic` SDK on the API. Brian leans toward a stream with these. Check two facts first: does Pydantic AI send the stream format of the AI SDK in a stable release, and does the Jev check run before the text shows or after the stream ends? The choice of Pydantic AI depends on decision 12, because it pays off only if Claude gets tools. The spec needs this, because a 25 s wait on the front door breaks the design bar.

## Decision

Partial. Brian, 2026-11-09: the site uses the Vercel AI SDK (`useChat`) to read the stream. Decision 12 set the server: Pydantic AI with `VercelAIAdapter`. The server side, the cache, the wait, the caps, and the Jev check stay open for this ticket.
