/**
 * The Goal switch of The Race: a playoff spot, a bye, or one seed, with the seed picker of 1 to the last seed under it.
 * It takes the Goal and the playoff spots and gives the next Goal on a tap. A league with no bye shows no Bye.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useMotionOff } from "@cpc/design/hooks/use-motion-off";
import { cn } from "@cpc/design/lib/utils";
import {
  SegmentedControl,
  SegmentedControlIndicator,
  SegmentedControlItem,
} from "@cpc/design/ui/segmented-control";
import { Toggle, ToggleGroup } from "@cpc/design/ui/toggle-group";
import { PRESS } from "./format";
import { type GoalKey, seedOf } from "./goals";

/* A chip of the seed picker. The picked chip turns to ink, so red keeps its one meaning on the page: Your team. */
const CHIP = cn(
  PRESS,
  "min-h-touch rounded-pill border-rule bg-card px-sp-2 text-row text-mute border font-bold tabular-nums",
  "hover-fine:text-ink transition-[background-color,border-color,color] duration-150 ease-out",
  "data-pressed:border-ink data-pressed:bg-ink data-pressed:text-page",
);

/* The seed picker rises 4 px into place on --ease-smooth-out, and fades out faster than it came in. */
const ENTER = { duration: 0.25, ease: [0.22, 1, 0.36, 1] } as const;

export function GoalSwitch({
  goal,
  onGoal,
  spots,
  bye,
}: {
  goal: GoalKey;
  onGoal: (goal: GoalKey) => void;
  spots: number;
  bye: boolean;
}) {
  const off = useMotionOff();
  const seed = seedOf(goal);
  const kind = seed === null ? goal : "seed";
  // A tap of Seed keeps the seed picked before, or opens on the 1 seed.
  const lastSeed = seed ?? 1;
  return (
    <div className="gap-sp-2 flex flex-col">
      <SegmentedControl<string>
        aria-label="Goal"
        value={kind}
        onValueChange={(next) => {
          if (next === null) return;
          onGoal(next === "seed" ? `seed-${lastSeed}` : (next as GoalKey));
        }}
      >
        <SegmentedControlIndicator />
        <SegmentedControlItem value="spot">Spot</SegmentedControlItem>
        {bye && <SegmentedControlItem value="bye">Bye</SegmentedControlItem>}
        <SegmentedControlItem value="seed">Seed</SegmentedControlItem>
      </SegmentedControl>
      <AnimatePresence initial={false}>
        {seed !== null && (
          <motion.div
            initial={off ? { opacity: 0 } : { opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, transition: { duration: 0.15 } }}
            transition={off ? { duration: 0.15 } : ENTER}
          >
            <ToggleGroup
              aria-label="Seed"
              value={[String(seed)]}
              onValueChange={(value: string[]) => value[0] && onGoal(`seed-${Number(value[0])}`)}
              className="gap-sp-1 grid"
              style={{ gridTemplateColumns: `repeat(${spots}, minmax(0, 1fr))` }}
            >
              {Array.from({ length: spots }, (_, i) => String(i + 1)).map((n) => (
                <Toggle key={n} value={n} aria-label={`Seed ${n}`} className={CHIP}>
                  {n}
                </Toggle>
              ))}
            </ToggleGroup>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
