# 37: Send closes the keyboard, and every dock tap works on the first tap

Spec: `.scratch/front-door/PRD.md`. Source: H22 and H23 of `.scratch/front-door/HANDS-ON.md`.

**App:** site

**What to build:** after Send, the field blurs, so the phone keyboard closes and the Answer shows. The first tap on the arrow still sends (ticket 34). A Suggestion chip, More, and any other tap target of the dock also work on the first tap, with the keyboard open or closed.

**Blocked by:** 34

**Status:** in-review

- [x] A test proves Send closes the keyboard after the question goes, and the first tap on Send still sends.
- [x] A test proves a tap on a chip, on More, and on a row of More works on the first tap while the field has focus.
- [x] A chip or a row of More closes the keyboard after it acts. More keeps it open.
- [x] On WebKit with a phone viewport and touch, one tap on a chip acts.

## Cause of H23

The cause is the cause of H20, on the chips. A press on a chip blurs the field at `mousedown`. The blur drops `data-keyboard`, and the dock drops under the thumb before the click lands. The WebKit run on an iPhone 15 viewport with a fake keyboard of 336 px logs: the chip at y=191 on `mousedown`, `focusout`, then `mouseup` on a `FORM` and `click` on a `DIV` at y=425, and no pick.

## Fix

`keyboard-tap.ts` holds two moves. `keepFocus` cancels the default of `mousedown`, and `closeKeyboard` blurs the field. Send, the chips, More, and the rows of More use `keepFocus`. Send, a chip, and a row of More call `closeKeyboard` after the action runs. The same WebKit run then logs `mousedown`, `mouseup`, and `click` on the chip at y=191, and `focusout` last. Proof: `ask-box.test.tsx`, `suggestions.test.tsx` (vitest), and `e2e/front-door.spec.ts` (floor project), all red before the fix.

The e2e test keeps a passphrase and fails the API calls. Without a passphrase, the card of the passphrase takes the focus after Send, so the test cannot show the keyboard close. The phone of the e2e test now runs with motion on, as a phone does.
