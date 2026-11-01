/**
 * The drift field of the waiver page: the top six of the open bucket as headshots that drift in slow motion, each with its price.
 * Each rank has a fixed slot from the layout table, and the drift stops under reduced motion and while the document is hidden.
 */
"use client";

import { motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import { shortName } from "@/lib/format/format";
import { sleeperHeadshot, swapToDefault } from "@/lib/headshot";
import { DRIFT_EASE, DURATION, INSTANT, rise, stagger, useMotionOff } from "@/lib/motion";
import { cn } from "@/lib/utils";
import type { BucketKey, WaiverPlayer } from "@/lib/waiver-types";
import { FIELD, fieldScale, LABEL, scaleSlot, SLOTS, TAG, type Slot } from "./field-layout";
import { priceText } from "./format";

/* False while the document is hidden, so a drift in a background tab does not drain the battery.
   The first render reads true, so the static HTML and the first client render match. */
function usePageVisible(): boolean {
  const [visible, setVisible] = useState(true);
  useEffect(() => {
    const read = () => setVisible(document.visibilityState !== "hidden");
    read();
    document.addEventListener("visibilitychange", read);
    return () => document.removeEventListener("visibilitychange", read);
  }, []);
  return visible;
}

/* The scale of the field in its column, measured once on mount. A phone under 390 gets a smaller field and no side scroll. */
function useFieldScale() {
  const ref = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  useEffect(() => {
    setScale(fieldScale(ref.current?.clientWidth ?? 0));
  }, []);
  return { ref, scale };
}

function Orb({
  player,
  slot,
  scale,
  index,
  open,
  drift,
  off,
  onOpen,
}: {
  player: WaiverPlayer;
  slot: Slot;
  scale: number;
  index: number;
  open: boolean;
  drift: boolean;
  off: boolean;
  onOpen: (player: WaiverPlayer) => void;
}) {
  const price = priceText(player);
  // The box is as wide as the headshot or the label, whichever is wider, and its center is the center of the slot.
  const width = Math.max(slot.size, LABEL.width * scale);
  return (
    // The outer box rises in once per bucket, and the inner box drifts. Each motion has its own box, so each owns its own transform.
    // data-reveal lets the safety rule in globals.css show the headshot if the script never loads.
    <motion.div
      data-reveal
      className="absolute"
      style={{ left: slot.x - width / 2, top: slot.y, width }}
      {...rise(off, { duration: DURATION.reveal, delay: stagger(index) })}
    >
      <motion.div
        animate={drift ? { x: [0, slot.dx], y: [0, slot.dy] } : { x: 0, y: 0 }}
        transition={drift ? { duration: slot.period, ease: DRIFT_EASE, repeat: Infinity, repeatType: "mirror" } : INSTANT}
      >
        <button
          type="button"
          aria-label={price ? `${player.name}, ${price}` : player.name}
          aria-pressed={open}
          onClick={() => onOpen(player)}
          className="press flex w-full cursor-pointer flex-col items-center border-0 bg-transparent p-0 text-inherit [-webkit-tap-highlight-color:transparent]"
        >
          <span className="relative block">
            {/* The geometry comes from the layout table, so the overlap test covers what the page draws. */}
            <img
              src={sleeperHeadshot(player.player_id)}
              alt=""
              onError={swapToDefault}
              style={{ width: slot.size, height: slot.size }}
              className={cn(
                // The fill is the dark rule, so it stays one step off the black card in both themes. Ink-2 turns light grey in the dark theme.
                "block rounded-full border-2 bg-rule-dark object-cover object-top shadow-orb",
                open ? "border-on-dark" : "border-red",
              )}
            />
            {price && (
              <span
                style={{ top: -TAG.up * scale, right: -TAG.out * scale }}
                // The price tag uses the page and its ink, so it inverts with the theme. Ink inverts with the page, so the chip text shows in both themes.
                className="absolute rounded-full bg-wht px-sp-1 py-sp-0 text-label leading-tight font-bold text-ink tabular-nums"
              >
                {price}
              </span>
            )}
          </span>
          <span className="mt-sp-1 block w-full truncate text-center text-meta leading-tight font-bold">{shortName(player.name)}</span>
          <span className="block text-label leading-tight text-on-dark-2">{`${player.position} · ${player.team}`}</span>
        </button>
      </motion.div>
    </motion.div>
  );
}

export function DriftField({
  bucket,
  players,
  openId,
  onOpen,
}: {
  bucket: BucketKey;
  players: WaiverPlayer[];
  openId: string | null;
  onOpen: (player: WaiverPlayer) => void;
}) {
  const off = useMotionOff();
  const visible = usePageVisible();
  const drift = !off && visible;
  const { ref, scale } = useFieldScale();
  return (
    // The outer box takes the column width, so the hook can measure it. It clips the field before the measure, so the page never scrolls sideways.
    <div ref={ref} className="w-full overflow-hidden">
      <div
        role="group"
        aria-label="Top six"
        data-drift={drift ? "on" : "off"}
        className="relative mx-auto"
        style={{ width: FIELD.width * scale, height: FIELD.height * scale }}
      >
        <div aria-hidden className="field-glow" />
        {players.slice(0, SLOTS.length).map((player, index) => (
          // The key holds the bucket, so a tab change mounts new headshots and they rise in again.
          <Orb
            key={`${bucket}-${player.player_id}`}
            player={player}
            slot={scaleSlot(SLOTS[index], scale)}
            scale={scale}
            index={index}
            open={player.player_id === openId}
            drift={drift}
            off={off}
            onOpen={onOpen}
          />
        ))}
      </div>
    </div>
  );
}
