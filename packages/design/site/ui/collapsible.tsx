/**
 * Collapsible primitive built on the ui-sdk Collapsible: a trigger that shows and hides one panel, which fades with a small rise.
 * It renders the root, the trigger, and the panel, and sets only the motion of the panel.
 */
"use client"

import * as React from "react"
import {
  Collapsible as Root,
  CollapsiblePanel as Panel,
  CollapsibleTrigger as Trigger,
} from "@ui-sdk/react/collapsible"
import { cn } from "../lib/utils"

function Collapsible({ ...props }: React.ComponentProps<typeof Root>) {
  return <Root {...props} />
}

function CollapsibleTrigger({ ...props }: React.ComponentProps<typeof Trigger>) {
  return <Trigger {...props} />
}

// The panel opens to its full height at once, then fades in and rises 4 px over 250 ms on cubic-bezier(0.22, 1, 0.36, 1),
// the --ease-smooth-out curve of transitions-dev. It closes with the same fade and drop. Site motion is transform and
// opacity only (ADR 0024), so the height never animates. Reduced motion keeps only the fade.
function CollapsiblePanel({ className, ...props }: React.ComponentProps<typeof Panel>) {
  return (
    <Panel
      className={cn(
        "transition-[opacity,transform] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] data-starting-style:opacity-0 data-ending-style:opacity-0 motion-safe:data-starting-style:translate-y-sp-1 motion-safe:data-ending-style:translate-y-sp-1",
        className,
      )}
      {...props}
    />
  )
}

export { Collapsible, CollapsiblePanel, CollapsibleTrigger }
