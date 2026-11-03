# src/components/ui: the shadcn primitives

## Knows

- The button, the dialog, the input, the label, the popover, and the select.
- Most of them wrap a Base UI primitive and add the site styles.
- The label is the form label. The red label that opens a chapter is `src/components/parts/label.tsx`.

## Ports

None.

## Does not do

- It knows no league term. A component that shows a team, a player, or a week is a part in `src/components/parts/`, or it lives in its page folder.
- It holds no state of the site.
- It holds no `cn` helper. `src/lib/utils.ts` holds it.
- It reads no file, no env, and no config, and it calls no loader (ADR 0012).
