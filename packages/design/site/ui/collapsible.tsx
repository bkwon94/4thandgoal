/**
 * Collapsible primitive built on the ui-sdk Collapsible: a trigger that shows and hides one panel, with its height animated.
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

// The panel grows from 0 to the height that the Collapsible measures, on --duration-fast and --ease-smooth-out, the
// accordion of transitions-dev. Reduced motion drops the height move, so the panel opens at once.
function CollapsiblePanel({ className, ...props }: React.ComponentProps<typeof Panel>) {
  return (
    <Panel
      className={cn(
        "h-(--collapsible-panel-height) overflow-hidden transition-[height] duration-250 ease-[cubic-bezier(0.22,1,0.36,1)] data-starting-style:h-0 data-ending-style:h-0 motion-reduce:transition-none",
        className,
      )}
      {...props}
    />
  )
}

export { Collapsible, CollapsiblePanel, CollapsibleTrigger }
