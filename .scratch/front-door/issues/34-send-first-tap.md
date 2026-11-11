# 34: The send arrow sends on the first tap

Spec: `.scratch/front-door/PRD.md`. Source: H20 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** on a phone, with the keyboard open, the first tap on the send arrow does nothing, and a second tap sends. Find the cause on a real mobile engine, then fix it so one tap sends.

**Blocked by:** none

**Status:** in-review

- [x] A test proves one tap on the send arrow sends while the field has focus.
- [x] On WebKit with a phone viewport and touch, one tap sends.

## Cause

The press on Send blurs the field at `mousedown`. The blur drops `data-keyboard`, so the dock comes back and the foot of the Thread drops from right above the keyboard to its place above the dock. `mouseup` and `click` then land on the page under the thumb, not on Send. The WebKit run on an iPhone 15 viewport with a fake keyboard of 336 px logs it: Send at y=262 on `mousedown`, `focusout`, then `mouseup` and `click` on a `DIV` at y=496, and no `submit`. The empty Thread holds the ask box at its center, so it does not move there.

## Fix

Send cancels the default of `mousedown`, so the field keeps the focus and the keyboard stays open. The same WebKit run then logs `mousedown`, `mouseup`, `click`, and `submit`, all on Send at y=262. Proof: `ask-box.test.tsx` (vitest) and `e2e/front-door.spec.ts` (floor project), both red before the fix.
