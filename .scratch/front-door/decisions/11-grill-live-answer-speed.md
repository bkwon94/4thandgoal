# 11: How does a live personal Answer stay fast and cheap?

Map: `.scratch/front-door/MAP.md`.

**Kind:** grill

**Blocked by:** 03

**Status:** done

## Question

The personal Topics are live (decision 01). One Claude answer takes about 20 to 27 s and costs about $0.04 to $0.10 (`03-research-jev-live-cost.notes.md`). Decide if the API keeps a personal Answer until the roster changes. Decide if a Suggestion builds its Answer before the tap. Decide what the manager sees during the wait. Decide also how the personal Answers count against the caps of decision 04. Decide if the Answer streams, and with which parts: the Vercel AI SDK (`useChat`) on the site, and Pydantic AI or the plain `anthropic` SDK on the API. Brian leans toward a stream with these. Check two facts first: does Pydantic AI send the stream format of the AI SDK in a stable release, and does the Jev check run before the text shows or after the stream ends? The choice of Pydantic AI depends on decision 12, because it pays off only if Claude gets tools. The spec needs this, because a 25 s wait on the front door breaks the design bar.

## Decision

Brian, 2026-11-09, in a grill.

1. The parts: the site reads the stream with `useChat` of the Vercel AI SDK. Pydantic AI runs Claude on the API and streams through `VercelAIAdapter` (decision 12).
2. The API keeps each Answer under a key built from the facts it read, such as the roster and the week. The same facts stream the kept Answer back at once, at no cost. A waiver claim or a trade changes the key, so Claude writes a fresh Answer. A free answer keys on the question text plus the data it read. Reason: the key keeps what is still true and drops what is stale. A fixed time shows a stale Answer after a trade.
3. On open, the front door builds the Answer of the top Suggestion only, if it is a personal Topic. The other Suggestions build on the tap. Cost: about $6 to $10 a month for 2 leagues. Reason: the top Suggestion takes most taps, for about a third of the cost of all 3.
4. The stream order: the data block of a Topic comes from code, needs no check, and shows at once. The text streams under it. The Jev check runs after the last word, and a small "checking" mark turns into "checked". If Jev fails a claim, the text fades out, "Fixing a number…" shows, and Claude writes once more with a new check. A second fail shows the honest miss. A free answer has no data block, so its text streams first.
5. The wait is transparent. Each tool call shows as a step, such as "Reading week 1…", so the wait reads as work. Brian: "stream is huge so we can have beautiful ui to help the wait feel shorter and be transparent w whats going on." Prototype 08 designs these steps to the design bar.
6. How the Answers count against the caps is decision 04.
