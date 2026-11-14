# A sheet you can drag follows a spring

ADR 0024 sets one motion rule for the site: transform and opacity only, a strong ease-out, and none under reduced motion. A sheet under the finger is different. It must follow the finger and settle as a native sheet does, and that feel is the goal of the move to ui-sdk (spec `ui-sdk-sheet`). So a sheet you can drag settles with a spring, and under reduced motion it may fade in and out in place of a slide. Every other motion keeps the rule of ADR 0024. We chose this over a forced ease-out because an ease-out under a drag feels dead. We allow the fade because it does not move the page, and it still shows where the sheet came from.

Amends ADR 0024 in part.

## Consequences

- A sheet uses the spring of the ui-sdk `Drawer`. A tune goes through its `physics` prop, never through a CSS transition on the translate.
- A sheet stays transform and opacity only. The `Drawer` moves it with `translate` and dims the page with opacity.
- Under reduced motion, a sheet fades and does not slide. No other part of the site fades under reduced motion.
