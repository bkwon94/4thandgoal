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

type StopCardProps = Omit<React.ComponentProps<typeof Popover>, "modal" | "presentation" | "dismissible">

/* What onDismissAttempt receives: the details of a refused dismiss, and its reason. */
type StopCardDismissDetails = Parameters<NonNullable<StopCardProps["onDismissAttempt"]>>[0]
type StopCardDismissReason = StopCardDismissDetails["reason"]

/* The part of the browser CloseWatcher that the card uses. A browser with no CloseWatcher, and jsdom, have none. */
type CloseWatcherLike = { addEventListener(type: "close", listener: (event: Event) => void): void; destroy(): void }
type CloseWatcherClass = new () => CloseWatcherLike

/* An Escape and its close request come this close together, as in the ui-sdk layers. */
const ESCAPE_CLOSE_MS = 100

/* The ui-sdk popover preset sets no close watcher, so Android Back never reaches onDismissAttempt. This hook registers
   a browser CloseWatcher while the card is open, and sends the reason "back" to onDismissAttempt. Chromium also sends a
   close request on Escape, after the keydown. The popover already reports that Escape as "escape-key", so a close
   request that comes right after an Escape is dropped, and each Escape counts once. */
function useBackAttempt(open: boolean | undefined, onDismissAttempt: StopCardProps["onDismissAttempt"]) {
  const attempt = React.useRef(onDismissAttempt)
  React.useEffect(() => {
    attempt.current = onDismissAttempt
  })
  React.useEffect(() => {
    const Watcher = (globalThis as { CloseWatcher?: CloseWatcherClass }).CloseWatcher
    if (!open || typeof Watcher !== "function") return
    let escapeAt = -Infinity
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") escapeAt = performance.now()
    }
    let watcher: CloseWatcherLike
    try {
      watcher = new Watcher()
    } catch {
      return
    }
    // A close request destroys its watcher. The card registers one watcher each time it opens, because the Tour ends
    // on Back and closes the card.
    watcher.addEventListener("close", (event) => {
      if (performance.now() - escapeAt >= ESCAPE_CLOSE_MS) attempt.current?.({ reason: "back", event })
    })
    document.addEventListener("keydown", onKey, true)
    return () => {
      document.removeEventListener("keydown", onKey, true)
      watcher.destroy()
    }
  }, [open])
}

// Modal, so the page is inert, the scroll locks, and focus stays in the card. Always a popover, because "auto" turns
// into a sheet on a phone. Not dismissible, so each Escape, each press outside, and each Android Back comes to
// onDismissAttempt, and the caller decides what it does.
function StopCard(props: StopCardProps) {
  useBackAttempt(props.open, props.onDismissAttempt)
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
export type { StopCardDismissDetails, StopCardDismissReason }
