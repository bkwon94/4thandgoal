/**
 * Segmented control built on the ui-sdk SegmentedControl: the root, the sliding indicator, and the items.
 * It is the one place the site imports the ui-sdk SegmentedControl. The items split the full width in equal parts.
 */
"use client"

import * as React from "react"
import {
  createSegmentedControlController,
  SegmentedControl as SdkSegmentedControl,
  SegmentedControlIndicator as SdkSegmentedControlIndicator,
  SegmentedControlItem as SdkSegmentedControlItem,
} from "@ui-sdk/react/segmented-control"
import { cn } from "../lib/utils"

// light sits on the page or a card. dark sits on the band color of a hero, which stays dark in both themes.
type Tone = "light" | "dark"

// The root names its tone in data-tone, so the indicator and each item read it through the seg group.
function SegmentedControl<T extends string = string>({
  className,
  tone = "light",
  ...props
}: React.ComponentProps<typeof SdkSegmentedControl<T>> & { tone?: Tone }) {
  return (
    <SdkSegmentedControl<T>
      data-tone={tone}
      className={cn(
        "group/seg relative isolate flex w-full gap-sp-1 rounded-pill p-sp-1",
        tone === "dark" ? "bg-chip-dark" : "bg-raised",
        className,
      )}
      {...props}
    />
  )
}

// The pill slides as the tabs sliding recipe of transitions.dev: 250 ms with the brand ease-out. Reduced motion jumps it.
function SegmentedControlIndicator({ className, ...props }: React.ComponentProps<typeof SdkSegmentedControlIndicator>) {
  return (
    <SdkSegmentedControlIndicator
      className={cn(
        "absolute top-(--segmented-control-indicator-top) left-(--segmented-control-indicator-left) -z-10 h-(--segmented-control-indicator-height) w-(--segmented-control-indicator-width) rounded-pill bg-card shadow-ask transition-[left,width] duration-250 ease-(--ease-out) motion-reduce:transition-none group-data-[tone=dark]/seg:bg-on-dark group-data-[tone=dark]/seg:shadow-none",
        className,
      )}
      {...props}
    />
  )
}

// basis-0 with flex-1 gives each item the same width whatever its label, so two items make two equal halves.
// A disabled unchecked item fades to 75%, not lower: on the dark tone, 60% put its text at 3.97:1 on the chip, under 4.5:1.
function SegmentedControlItem({ className, ...props }: React.ComponentProps<typeof SdkSegmentedControlItem>) {
  return (
    <SdkSegmentedControlItem
      className={cn(
        "press flex min-h-touch min-w-0 flex-1 basis-0 cursor-pointer items-center justify-center rounded-pill px-sp-2 text-row font-bold whitespace-nowrap text-mute outline-none focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent data-[checked]:text-ink data-[disabled]:cursor-not-allowed data-[disabled]:data-[unchecked]:opacity-75 group-data-[tone=dark]/seg:text-on-dark-2 group-data-[tone=dark]/seg:data-[checked]:text-band",
        className,
      )}
      {...props}
    />
  )
}

// The controller focuses or checks an item from outside, such as a switch that a new hero mounts in place of the old one.
export { createSegmentedControlController, SegmentedControl, SegmentedControlIndicator, SegmentedControlItem }
