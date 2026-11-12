/**
 * One row of a Ledger block that opens in place: the head with a chevron, and its detail under it on the Open card of
 * the site. A live row rises in on the stagger of the rows, and a kept row shows at once.
 */
"use client";

import { motion } from "framer-motion";
import type { ReactNode } from "react";
import { ChevronDown } from "lucide-react";
import { OpenCard } from "@cpc/design/parts/open-card";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { VERY_SLOW, riseIn, staggerOf } from "./motion";

/* The quiet mono label over a Ledger block, as the label of the list block. */
export function LedgerLabel({ id, children }: { id?: string; children: ReactNode }) {
  return (
    <p id={id} className="m-0 truncate font-mono text-meta leading-tight tracking-caps text-mute uppercase">
      {children}
    </p>
  );
}

/* A row keeps its place: it grows taller in place on open, and its detail comes into focus from a blur, so no other row
   changes its order. The head is the one toggle, and the chevron turns with the height. With motion off, the Open card
   opens at once and the row only fades in. */
export function LedgerRow({ panelId, label, live, index, head, children }: { panelId: string; label: string; live: boolean; index: number; head: ReactNode; children: ReactNode }) {
  const off = useMotionOff();
  // The words of the lead line sweep in for up to --duration-very-slow, so the rows start as they settle.
  const motionProps = live ? riseIn(off, { text: true, delay: VERY_SLOW * 0.6 + staggerOf(index + 1) }) : {};
  return (
    <motion.li aria-label={label} className="list-none" {...motionProps}>
      <OpenCard
        as="div"
        look="row"
        panelId={panelId}
        headClassName="border-b border-rule py-sp-2"
        head={
          <span className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3">
            <span className="min-w-0">{head}</span>
            <ChevronDown aria-hidden className="oc-chevron size-sp-4 text-mute" strokeWidth={2} />
          </span>
        }
      >
        {children}
      </OpenCard>
    </motion.li>
  );
}
