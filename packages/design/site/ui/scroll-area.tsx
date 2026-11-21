/**
 * Scroll area built on the ui-sdk ScrollArea: the root, the viewport that the browser scrolls, and the content.
 * It is the one place the site imports the ui-sdk ScrollArea. The browser keeps its own scroll, so touch, wheel, and keys work.
 */
"use client"

import * as React from "react"
import {
  ScrollArea as Root,
  ScrollAreaContent as Content,
  ScrollAreaViewport as Viewport,
} from "@ui-sdk/react/scroll-area"

// The root and the content pass through. A part sets its own size, mask, and padding with its class.
function ScrollArea(props: React.ComponentProps<typeof Root>) {
  return <Root {...props} />
}

function ScrollAreaViewport(props: React.ComponentProps<typeof Viewport>) {
  return <Viewport {...props} />
}

function ScrollAreaContent(props: React.ComponentProps<typeof Content>) {
  return <Content {...props} />
}

export { ScrollArea, ScrollAreaContent, ScrollAreaViewport }
