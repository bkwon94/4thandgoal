/**
 * The Announcement: a bottom sheet on the shared Sheet that introduces a new feature once. From the top it holds the art
 * slot, the eyebrow, the title, one line, the link to the feature, and "Not now". The use fills the art and the copy.
 * Use it when: one new feature needs a one-time introduction.
 * Do not use it when: the sheet needs an answer from the reader. Use `Dialog`.
 */
"use client";

import { motion } from "framer-motion";
import { ArrowRightIcon } from "lucide-react";
import { type ReactNode, useEffect, useRef, useState } from "react";
import { useMotionOff } from "../hooks/use-motion-off";
import { Sheet, SheetBackdrop, SheetClose, SheetContent, SheetGrip, SheetTitle } from "../ui/sheet";

export type AnnouncementCopy = {
  eyebrow: string;
  title: string;
  line: string;
  // The label of the link to the feature.
  follow: string;
  dismiss: string;
};

/* The entry of the eyebrow, the title, and the line: a short rise on --ease-smooth-out, one after the other, after the
   sheet has most of its way up. Under reduced motion the words show at once, and the Drawer fades the sheet. */
const SMOOTH = [0.22, 1, 0.36, 1] as const;
const riseIn = (off: boolean, index: number) =>
  off
    ? { initial: false as const }
    : {
        initial: { opacity: 0, y: 8 },
        animate: { opacity: 1, y: 0 },
        transition: { duration: 0.35, ease: SMOOTH, delay: 0.12 + index * 0.04 },
      };

/* The parent owns `open`. Any close reaches onDismiss: "Not now", Escape, a tap on the dim, or a drag down. A press of the
   link reaches onFollow, and the browser then follows the link. onSettled runs once the sheet stops on open, so the art can
   start a move that the eye must see. The Drawer owns the slide, the drag, the dim, the focus trap, and Escape. */
export function Announcement({
  open,
  siteName,
  href,
  copy,
  art,
  onDismiss,
  onFollow,
  onSettled,
}: {
  open: boolean;
  siteName: string;
  href: string;
  copy: AnnouncementCopy;
  art: ReactNode;
  onDismiss: () => void;
  onFollow: () => void;
  onSettled?: () => void;
}) {
  const off = useMotionOff();
  // A drag down reports its close twice, so the sheet reports one dismiss per open.
  const closed = useRef(false);
  // The Drawer runs no open and reports no stop for a sheet that mounts open. So the sheet mounts closed, and opens on
  // the next render.
  const [shown, setShown] = useState(false);
  useEffect(() => {
    if (open) closed.current = false;
    setShown(open);
  }, [open]);
  return (
    <Sheet
      side="bottom"
      open={shown}
      onOpenChange={(next) => {
        if (next || closed.current) return;
        closed.current = true;
        onDismiss();
      }}
      onOpenChangeComplete={(next) => {
        if (next) onSettled?.();
      }}
      container={typeof document === "undefined" ? undefined : document.body}
    >
      <SheetBackdrop />
      {/* Focus lands on the sheet itself, so the first control of the art shows no focus ring on open. Tab then reaches
          each control. */}
      <SheetContent
        initialFocus="content"
        aria-describedby="announcement-line"
        // The sheet never reaches the top of a short phone, so the dim above it still reads as the page to come back to.
        className="max-w-sheet rounded-t-hero border-rule bg-card shadow-sheet mx-auto flex max-h-[calc(100dvh-env(safe-area-inset-top)-var(--spacing-sp-6))] w-full flex-col border border-b-0"
      >
        <SheetGrip className="mt-sp-2 h-sp-1 w-sp-6" />
        {/* The art and the words scroll inside the sheet on a very short screen. The actions stay in their own row. */}
        <div className="gap-sp-4 px-sp-4 pt-sp-3 flex min-h-0 flex-col overflow-y-auto overscroll-contain">
          {art}
          <div className="gap-sp-1 px-sp-1 flex flex-col">
            <motion.span
              {...riseIn(off, 0)}
              className="text-meta tracking-caps text-accent-ink font-mono leading-tight font-bold uppercase"
            >
              {/* The site name is in the prop, not in the art, so a screen reader hears whose note it is (ADR 0012). */}
              <span className="sr-only">{`${siteName}: `}</span>
              {copy.eyebrow}
            </motion.span>
            <motion.div {...riseIn(off, 1)}>
              <SheetTitle className="text-score m-0 leading-tight font-bold tracking-tight text-balance">
                {copy.title}
              </SheetTitle>
            </motion.div>
            <motion.p
              {...riseIn(off, 2)}
              id="announcement-line"
              className="text-lead leading-body text-ink-2 m-0 text-pretty"
            >
              {copy.line}
            </motion.p>
          </div>
        </div>
        {/* The end of the sheet keeps the home bar of an iPhone clear. */}
        <div className="gap-sp-1 px-sp-5 pt-sp-4 flex flex-none flex-col pb-[calc(var(--spacing-sp-2)+env(safe-area-inset-bottom))]">
          <a
            href={href}
            onClick={onFollow}
            className="press min-h-touch gap-sp-2 rounded-pill bg-accent px-sp-5 text-body text-on-dark focus-visible:outline-ink flex items-center justify-center leading-tight font-semibold no-underline outline-none focus-visible:outline-2 focus-visible:outline-offset-2"
          >
            {copy.follow}
            <ArrowRightIcon aria-hidden className="size-sp-4" strokeWidth={2.25} />
          </a>
          <SheetClose className="press min-h-touch rounded-pill px-sp-4 text-meta text-mute hover-fine:text-ink focus-visible:outline-ink flex items-center justify-center self-center leading-tight font-semibold outline-none focus-visible:outline-2 focus-visible:outline-offset-2">
            {copy.dismiss}
          </SheetClose>
        </div>
      </SheetContent>
    </Sheet>
  );
}
