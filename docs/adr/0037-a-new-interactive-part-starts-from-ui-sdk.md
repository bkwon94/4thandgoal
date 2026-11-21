# A new interactive part starts from ui-sdk

The site mixes two sources of interactive parts: shadcn parts such as `button.tsx`, and ui-sdk parts such as `sheet.tsx`. A mix gives two ways to do focus, keyboard, and ARIA. We decided that ui-sdk is the standard for the frontend. A new interactive part, such as a switch, a tab set, or a menu, uses the ui-sdk part through its one wrapper in `packages/design/site/ui/` (ADR 0035), when ui-sdk ships that part. Brian decided it on 2026-11-19, when the Finder switch of the analyzer hero took the ui-sdk `SegmentedControl` (spec `deadline-week`, decision 07).

## Consequences

- A part that ui-sdk does not ship may be built by hand, or from `@ui-sdk/core`, per the `ui-sdk` skill.
- An old shadcn part stays until a ticket changes it. That ticket moves it to ui-sdk, so no spec rewrites old parts for their own sake.
- A prototype may build a part by hand for speed. Its spec uses the ui-sdk part.
