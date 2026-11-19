/**
 * The Stop card of the Tour, built on the ui-sdk Popover: modal, with no trigger, always a popover and never a sheet.
 * It renders the root, the content, the title, and the line. The caller places the card itself.
 */
"use client"

import * as React from "react"
import {
  Popover,
  PopoverContent,
  PopoverDescription,
  PopoverTitle,
} from "@ui-sdk/react/popover"
import { cn } from "../lib/utils"

// Modal, so the page is inert, the scroll locks, and focus stays in the card. Always a popover, because "auto" turns
// into a sheet on a phone. Not dismissible, so each Escape and each press outside comes to onDismissAttempt, and the
// caller decides what it does.
function StopCard(
  props: Omit<React.ComponentProps<typeof Popover>, "modal" | "presentation" | "dismissible">,
) {
  return <Popover modal presentation="popover" dismissible={false} {...props} />
}

// The content is a browser popover, so the class drops the margin, the border, the pad, and the fill that a browser
// gives one. The caller sets the place, because the ui-sdk positioner lags a moving hole.
function StopCardContent({
  className,
  ...props
}: React.ComponentProps<typeof PopoverContent>) {
  return (
    <PopoverContent
      className={cn("m-0 overflow-visible border-0 bg-transparent p-0 text-ink outline-none", className)}
      {...props}
    />
  )
}

// The title names the card, so a screen reader says the name of the Stop.
function StopCardTitle(props: React.ComponentProps<typeof PopoverTitle>) {
  return <PopoverTitle {...props} />
}

// The line describes the card.
function StopCardLine(props: React.ComponentProps<typeof PopoverDescription>) {
  return <PopoverDescription {...props} />
}

export { StopCard, StopCardContent, StopCardLine, StopCardTitle }
