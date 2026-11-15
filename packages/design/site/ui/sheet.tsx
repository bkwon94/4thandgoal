/**
 * Sheet primitive built on the ui-sdk Drawer. It is the one place the site imports ui-sdk.
 * It renders the root, trigger, backdrop, content, grip, title, and close parts of an edge sheet.
 */
"use client"

import * as React from "react"
import {
  Drawer,
  DrawerBackdrop,
  DrawerClose,
  DrawerContent,
  DrawerTitle,
  DrawerTrigger,
} from "@ui-sdk/react/drawer"
import { cn } from "../lib/utils"

// The root takes every option of the Drawer, such as side, snapPoints, physics, and persistentElements.
function Sheet({ ...props }: React.ComponentProps<typeof Drawer>) {
  return <Drawer {...props} />
}

function SheetTrigger({ ...props }: React.ComponentProps<typeof DrawerTrigger>) {
  return <DrawerTrigger {...props} />
}

// The Drawer writes the opacity of the backdrop inline from --drawer-dim, so the class never sets it. The backdrop is a
// popover, so the class drops the size, margin, border, and pad that a browser gives a popover.
function SheetBackdrop({
  className,
  ...props
}: React.ComponentProps<typeof DrawerBackdrop>) {
  return (
    <DrawerBackdrop
      className={cn("fixed inset-0 z-50 m-0 size-auto max-h-none max-w-none border-0 bg-scrim p-0", className)}
      {...props}
    />
  )
}

// The Drawer places the content and moves it with translate, so the class sets only the surface. data-side names the
// edge the sheet comes from. A sheet from the top rounds its bottom corners, and its shadow falls down onto the dim.
function SheetContent({
  className,
  ...props
}: React.ComponentProps<typeof DrawerContent>) {
  return (
    <DrawerContent
      className={cn(
        "border-rule bg-page text-ink outline-none data-[side=top]:rounded-b-card data-[side=top]:border-b data-[side=top]:shadow-drop",
        className,
      )}
      {...props}
    />
  )
}

// The grip shows that the sheet drags. A sheet with one snap point takes this plain bar, not the handle button of the
// Drawer, because a press on that button has no other place to move the sheet to.
function SheetGrip({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      aria-hidden
      data-slot="sheet-grip"
      className={cn("mx-auto h-1.5 w-10 flex-none rounded-pill bg-rule", className)}
      {...props}
    />
  )
}

function SheetTitle({ ...props }: React.ComponentProps<typeof DrawerTitle>) {
  return <DrawerTitle {...props} />
}

function SheetClose({ ...props }: React.ComponentProps<typeof DrawerClose>) {
  return <DrawerClose {...props} />
}

export {
  Sheet,
  SheetBackdrop,
  SheetClose,
  SheetContent,
  SheetGrip,
  SheetTitle,
  SheetTrigger,
}
