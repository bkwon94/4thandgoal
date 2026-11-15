/**
 * Sheet primitive built on the ui-sdk Drawer. It is the one place the site imports ui-sdk.
 * It renders the root, trigger, backdrop, content, handle, title, and close parts of an edge sheet.
 */
"use client"

import * as React from "react"
import {
  Drawer,
  DrawerBackdrop,
  DrawerClose,
  DrawerContent,
  DrawerHandle,
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

// The Drawer sets the opacity of the backdrop from --drawer-dim, so the class sets only the color.
function SheetBackdrop({
  className,
  ...props
}: React.ComponentProps<typeof DrawerBackdrop>) {
  return (
    <DrawerBackdrop
      className={cn("fixed inset-0 z-50 bg-black", className)}
      {...props}
    />
  )
}

// The Drawer places the content and moves it with translate, so the class sets only the surface.
function SheetContent({
  className,
  ...props
}: React.ComponentProps<typeof DrawerContent>) {
  return (
    <DrawerContent
      className={cn("bg-background text-foreground outline-none", className)}
      {...props}
    />
  )
}

function SheetHandle({
  className,
  ...props
}: React.ComponentProps<typeof DrawerHandle>) {
  return (
    <DrawerHandle
      className={cn("mx-auto my-2 block h-1.5 w-10 rounded-full bg-muted-foreground/40", className)}
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
  SheetHandle,
  SheetTitle,
  SheetTrigger,
}
