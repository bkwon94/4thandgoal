/**
 * Pending button built on the ui-sdk Button. It is the one place the site imports the ui-sdk Button.
 * A handler that returns a Promise keeps the button pending, with focus kept, until the Promise settles.
 * Use it when: a press starts async work and the button must wait until it ends.
 * Do not use it when: the action ends at once. Use `Button`.
 */
"use client";

import * as React from "react";
import { Button } from "@ui-sdk/react/button";

// It has its own name because ui/button.tsx is the shadcn button that other parts use. The Button gives
// aria-busy, aria-disabled, and data-pending while pending, so the label stays and the class styles the state.
function PendingButton({ ...props }: React.ComponentProps<typeof Button>) {
  return <Button {...props} />;
}

export { PendingButton };
