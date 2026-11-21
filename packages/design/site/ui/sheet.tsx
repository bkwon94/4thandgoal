/**
 * Sheet primitive built on the ui-sdk Drawer. It is the one place the site imports ui-sdk.
 * It renders the root, trigger, backdrop, content, grip, title, and close parts of an edge sheet.
 * Use it when: a panel comes in from an edge and the reader drags it closed.
 * Do not use it when: the panel is a centered modal. Use `Dialog`.
 */
"use client";

import * as React from "react";
import {
  Drawer,
  DrawerBackdrop,
  DrawerClose,
  DrawerContent,
  DrawerTitle,
  DrawerTrigger,
} from "@ui-sdk/react/drawer";
import { cn } from "../lib/utils";

// The root takes every option of the Drawer, such as side, snapPoints, physics, and persistentElements.
function Sheet({ ...props }: React.ComponentProps<typeof Drawer>) {
  return <Drawer {...props} />;
}

function SheetTrigger({ ...props }: React.ComponentProps<typeof DrawerTrigger>) {
  return <DrawerTrigger {...props} />;
}

// The Drawer writes the opacity of the backdrop inline from --drawer-dim, so the class never sets it. The backdrop is a
// popover, so the class drops the size, margin, border, and pad that a browser gives a popover.
function SheetBackdrop({ className, ...props }: React.ComponentProps<typeof DrawerBackdrop>) {
  return (
    <DrawerBackdrop
      className={cn(
        "bg-scrim fixed inset-0 z-50 m-0 size-auto max-h-none max-w-none border-0 p-0",
        className,
      )}
      {...props}
    />
  );
}

// The Drawer places the content and moves it with translate, so the class sets only the surface. data-side names the
// edge the sheet comes from. A sheet from the top rounds its bottom corners, and its shadow falls down onto the dim.
// A drag past the open height stretches the sheet by less than 24 px, as a rubber band. The bleed of a top or bottom
// sheet is a 6rem block of the sheet color past its anchored edge, so that stretch never lifts the edge off the screen.
// The ui-sdk default look has the same bleed, but the site does not load that look. A class that clips the overflow of
// the sheet also clips the bleed.
// The bleed is a child element, not a pseudo-element of the content. axe cannot find the background of a text inside a
// box with a large pseudo-element, and it then gives an incomplete color-contrast result, which fails the floor. The
// bleed comes first, so a consumer class such as space-y never puts a margin on it.
function SheetContent({
  className,
  children,
  ...props
}: React.ComponentProps<typeof DrawerContent>) {
  return (
    <DrawerContent
      className={cn(
        "group/sheet border-rule bg-page text-ink data-[side=top]:rounded-b-card data-[side=top]:shadow-drop relative outline-none data-[side=top]:border-b",
        className,
      )}
      {...props}
    >
      {/* The Drawer takes children as nodes or as a function of its state, so the bleed goes first in both forms. */}
      {typeof children === "function" ? (
        (state) => (
          <>
            {sheetBleed}
            {children(state)}
          </>
        )
      ) : (
        <>
          {sheetBleed}
          {children}
        </>
      )}
    </DrawerContent>
  );
}

const sheetBleed = (
  <div
    aria-hidden
    data-slot="sheet-bleed"
    className="pointer-events-none absolute -inset-x-px hidden h-[6rem] bg-inherit group-data-[side=bottom]/sheet:top-full group-data-[side=bottom]/sheet:block group-data-[side=top]/sheet:bottom-full group-data-[side=top]/sheet:block"
  />
);

// The grip shows that the sheet drags. A sheet with one snap point takes this plain bar, not the handle button of the
// Drawer, because a press on that button has no other place to move the sheet to.
function SheetGrip({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      aria-hidden
      data-slot="sheet-grip"
      className={cn("rounded-pill bg-rule mx-auto h-1.5 w-10 flex-none", className)}
      {...props}
    />
  );
}

function SheetTitle({ ...props }: React.ComponentProps<typeof DrawerTitle>) {
  return <DrawerTitle {...props} />;
}

function SheetClose({ ...props }: React.ComponentProps<typeof DrawerClose>) {
  return <DrawerClose {...props} />;
}

export { Sheet, SheetBackdrop, SheetClose, SheetContent, SheetGrip, SheetTitle, SheetTrigger };
