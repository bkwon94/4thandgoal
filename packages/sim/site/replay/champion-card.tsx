/**
 * The champion card that ends a replay: it sits above the complete bracket, the avatar scales up on a spring, the trophy
 * drops in, and the rays and a ring burst once. It names the title odds of the team over all runs.
 */
import { motion } from "framer-motion";
import { Trophy } from "lucide-react";
import { thousands } from "@cpc/design/format/format";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { enter, type Pace } from "./pace";
import type { Champion } from "./season";

/* The rays: thin wedges of the accent around the avatar, as a conic gradient. */
const RAYS = "repeating-conic-gradient(from 0deg, var(--color-accent) 0deg 4deg, transparent 4deg 18deg)";

export function ChampionCard({
  champion,
  runs,
  pace,
}: {
  champion: Champion;
  // The count of all runs of the sim.
  runs: number;
  pace: Pace;
}) {
  // The burst moves and scales, so it plays only with full motion and never after a skip.
  const burst = !pace.off && !pace.still;
  return (
    <motion.div
      role="group"
      aria-label="Champion of This Run"
      {...enter(pace, { scale: 0.96 }, { duration: 0.4 })}
      // The card sits in the flow of the stage above the bracket, so the final state shows both. It clips the rays.
      className="relative flex flex-col items-center gap-sp-3 overflow-hidden px-sp-4 text-center"
    >
      <div className="relative flex items-center justify-center p-sp-6">
        {burst && (
          <>
            <motion.span
              aria-hidden="true"
              className="pointer-events-none absolute inset-[-40%] rounded-full"
              style={{ background: RAYS }}
              initial={{ opacity: 0, rotate: 0, scale: 0.6 }}
              animate={{ opacity: [0, 0.5, 0], rotate: 30, scale: 1.1 }}
              transition={{ duration: 1.2, delay: 0.3, ease: "easeOut" }}
            />
            <motion.span
              aria-hidden="true"
              className="pointer-events-none absolute inset-0 rounded-full border-2 border-accent"
              initial={{ opacity: 1, scale: 0.6 }}
              animate={{ opacity: 0, scale: 1.8 }}
              transition={{ duration: 0.9, delay: 0.3, ease: "easeOut" }}
            />
          </>
        )}
        <motion.span data-avatar {...enter(pace, { scale: 0.4 }, { spring: true, delay: 0.1 })} className="relative">
          <PhotoFrame src={null} name={champion.name} size="lg" decorative />
        </motion.span>
        {/* The trophy drops in to the top of the box, centered over the avatar. */}
        <motion.span
          data-trophy
          aria-hidden="true"
          {...enter(pace, { y: -24 }, { spring: true, delay: 0.35 })}
          className="absolute top-0 left-1/2 -translate-x-1/2 text-accent-text"
        >
          <Trophy className="size-sp-6" strokeWidth={2.5} />
        </motion.span>
      </div>
      <motion.div {...enter(pace, {}, { duration: 0.4, delay: 0.5 })} className="flex flex-col items-center gap-sp-1">
        <span className="font-mono text-meta font-bold tracking-caps text-accent-text uppercase">Champion of This Run</span>
        <span className="text-score leading-tight font-bold text-on-dark">{champion.name}</span>
        <span className="text-body text-on-dark-2">{`Wins the title in ${champion.title}% of all ${thousands(runs)} runs`}</span>
      </motion.div>
    </motion.div>
  );
}
