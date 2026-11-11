# 01: Does TypeSafe Jev take images, and with what limits?

Map: `.scratch/evidence-flags/MAP.md`.

**Kind:** research

**Blocked by:** none

**Status:** done

## Question

A third question asks if a screenshot shows text that is cut off or that overflows. It would catch defects such as AT-41 of easter-eggs, the banner cut at 375, and the pill bar overflow at 1280 that reached CI. The `Jev` port in `packages/league/python/src/league/jev_port.py` takes a text state only. Find out if the TypeSafe API and `typesafe-sdk` take an image, in what format, at what size limit, and at what cost. If Jev takes no image, this question moves to OUT OF SCOPE. If it does, the spec adds the image input to the port.

## Decision

Jev takes images, so the screenshot question is in scope. The notes are in `decisions/01-research-jev-image-input.notes.md`.

- The installed `typesafe-sdk` 0.7.5 has `typesafe_sdk.Image`, so no upgrade is needed. All four question kinds take an image.
- The API takes PNG and JPEG only, 280 to 1568 px per side, 16 MiB per image, and 32 MiB per request. It never resizes an image.
- A full-page shot of the runner is taller than 1568 px, so the caller must cut or scale each shot first.
- An image costs input tokens at the text price. The token count per image is not confirmed yet.
- The `Jev` port gets its own image type, so a caller never imports the SDK. `TypeSafeJev` wraps it in `typesafe_sdk.Image`, and `FakeJev` accepts it.

The research agent found it on 2026-11-10. The ticket said that a yes puts the question in scope, so Brian made no new choice.
