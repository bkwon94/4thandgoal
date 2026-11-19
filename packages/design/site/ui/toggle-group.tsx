/**
 * Toggle group built on the ui-sdk Toggle. It is the one place the site imports the ui-sdk Toggle.
 * The group holds one shared value, one tab stop, and the arrow keys between its toggles.
 */
"use client"

import * as React from "react"
import { Toggle as SdkToggle, ToggleGroup as SdkToggleGroup } from "@ui-sdk/react/toggle"

// The group and each toggle report their state with aria-pressed and data-pressed, so the class of a part styles
// the pressed state. A part passes no style of its own here.
function ToggleGroup<T extends string = string>(props: React.ComponentProps<typeof SdkToggleGroup<T>>) {
  return <SdkToggleGroup<T> {...props} />
}

function Toggle(props: React.ComponentProps<typeof SdkToggle>) {
  return <SdkToggle {...props} />
}

export { Toggle, ToggleGroup }
