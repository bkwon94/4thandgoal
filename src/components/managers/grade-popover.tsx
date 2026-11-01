/**
 * The grade letter of the manager hero as a button, and the popover it opens with the grade in words and the rank on each part.
 * A click, a tap, or the keyboard opens it, never a hover alone, so it works the same on a phone and on a desktop.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { Popover, PopoverClose, PopoverContent, PopoverTitle, PopoverTrigger } from "@/components/ui/popover";
import { ordinal } from "@/lib/format/format";
import type { GradePart, ManagerGrade } from "@/lib/manager-types";
import { useMotionOff } from "@/hooks/use-motion-off";
import { DURATION, EASE_OUT, INSTANT } from "@/lib/motion";

/* The name of each part of the grade, keyed by the key in the file. A new part is one more line here. */
const PART_NAMES: Record<GradePart["key"], string> = {
  projection: "Projection Ahead",
  production: "Season Production",
  trade_value: "Trade Value",
  depth: "Depth And Holes",
};

/* The scale the popover starts from. It matches the Past Weeks popover, so the popover grows out of the letter and does not pop. */
const POPOVER_SCALE = 0.95;

/* The quiet mark beside the Grade label: a circled "i" that tells the letter opens more.
   It is an image with no text, so the label text stays "Grade". The button carries the name, so the mark is hidden from a screen reader. */
export function GradeMark() {
  return (
    <svg
      aria-hidden
      viewBox="0 0 16 16"
      className="ml-sp-1 inline-block size-[1em] align-[-0.125em] text-mute"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
    >
      <circle cx="8" cy="8" r="6.75" />
      <path d="M8 7.25v4" strokeLinecap="round" />
      <circle cx="8" cy="4.75" r="0.9" fill="currentColor" stroke="none" />
    </svg>
  );
}

export function GradePopover({ grade, teams }: { grade: ManagerGrade; teams: number }) {
  const off = useMotionOff();
  const [open, setOpen] = useState(false);
  // The popover leaves faster than it enters, along the same path. With motion off it leaves at once.
  const exit = off
    ? { opacity: 0, transition: INSTANT }
    : { opacity: 0, scale: POPOVER_SCALE, transition: { duration: DURATION.popoverExit, ease: EASE_OUT } };
  return (
    // Focus stays inside the open popover, as it does in the Past Weeks one. The page still scrolls and takes a tap outside.
    <Popover open={open} onOpenChange={setOpen} modal="trap-focus">
      {/* The button keeps the look of the plain letter: the size, the weight, and the color come from the number around it. */}
      <PopoverTrigger
        aria-label={`Grade ${grade.letter}, how the grade reads`}
        className="press m-0 cursor-pointer border-0 bg-transparent p-0 font-[inherit] leading-[inherit] text-inherit focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red"
      >
        {grade.letter}
      </PopoverTrigger>
      {/* Framer Motion owns the scale and the fade, so the CSS keyframes and the CSS transition of the primitive are off,
          for the same WebKit blink that the Past Weeks popover avoids. The collision padding keeps the popover
          one gutter inside the viewport, and the width never runs past two gutters on a phone. */}
      <AnimatePresence>
        {open && (
          <PopoverContent
            keepMounted
            align="start"
            sideOffset={8}
            collisionPadding={16}
            className="w-[min(20rem,calc(100vw-2*var(--spacing-gutter)))] gap-sp-4 rounded-none p-sp-4 transition-none data-open:animate-none data-closed:animate-none"
            render={
              <motion.div
                initial={off ? false : { opacity: 0, scale: POPOVER_SCALE }}
                animate={{ opacity: 1, scale: 1 }}
                exit={exit}
                transition={off ? INSTANT : { duration: DURATION.popover, ease: EASE_OUT }}
              />
            }
          >
            <PopoverTitle className="m-0 text-label leading-tight font-semibold tracking-caps text-mute uppercase">
              How The Grade Reads
            </PopoverTitle>
            {/* The read comes first: the grade in words, from the pipeline, so a reader gets the gist before the ranks. */}
            <p className="m-0 text-body text-ink">{grade.read}</p>
            {/* One line per part. The rank is the one emphasis, so the part name and "of 12" stay quiet. */}
            <ul className="m-0 flex list-none flex-col gap-sp-2 p-0 text-body text-ink-2 tabular-nums">
              {grade.parts.map((part) => (
                <li key={part.key}>
                  {`${PART_NAMES[part.key]} · `}
                  <span className="font-semibold text-ink">{ordinal(part.rank)}</span>
                  <span className="text-mute">{` of ${teams}`}</span>
                </li>
              ))}
            </ul>
            {/* Base UI asks for a close control in a popover that traps focus, so a touch screen reader can leave it.
                A keyboard closes the popover with Escape, so Tab skips the control, and it shows to no one. */}
            <PopoverClose tabIndex={-1} className="sr-only">
              Close How The Grade Reads
            </PopoverClose>
          </PopoverContent>
        )}
      </AnimatePresence>
    </Popover>
  );
}
