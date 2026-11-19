/**
 * The switch at the top of the analyzer hero: Grade a trade and Find a trade, in two equal halves across the hero.
 * It is the segmented control wrapper on the dark tone, so the lit pill slides between the halves.
 */
"use client";

import { useEffect, useState } from "react";
import {
  createSegmentedControlController,
  SegmentedControl,
  SegmentedControlIndicator,
  SegmentedControlItem,
} from "@cpc/design/ui/segmented-control";
import type { AnalyzerMode } from "../lib/mode";

const MODES: { value: AnalyzerMode; label: string }[] = [
  { value: "grade", label: "Grade a trade" },
  { value: "find", label: "Find a trade" },
];

/* Each mode has its own hero, so a tap mounts a new switch in the new hero. `from` is the mode that the old switch
   showed: the new switch paints on it first, then moves to `value` one frame later, so the pill slides across as in
   one control. With no change of mode, `from` equals `value` and nothing moves. */
export function ModeSwitch({
  value,
  from = value,
  onChange,
  disabled,
}: {
  value: AnalyzerMode;
  from?: AnalyzerMode;
  onChange: (mode: AnalyzerMode) => void;
  disabled: boolean;
}) {
  const [shown, setShown] = useState(from);
  const [controller] = useState(() => createSegmentedControlController<AnalyzerMode>());
  // The old switch left the page with its hero, and focus with it. A keyboard reader keeps focus on the new switch.
  const [moved] = useState(from !== value);
  useEffect(() => {
    if (moved && shown === value && document.activeElement === document.body) controller.focus();
  }, [moved, shown, value, controller]);
  useEffect(() => {
    if (shown === value) return;
    // Two frames: the first paints the pill at `from`, so the move to `value` runs as a transition.
    let id = requestAnimationFrame(() => {
      id = requestAnimationFrame(() => setShown(value));
    });
    return () => cancelAnimationFrame(id);
  }, [shown, value]);
  return (
    <SegmentedControl<AnalyzerMode> aria-label="Mode" tone="dark" value={shown} controller={controller} onValueChange={(next) => next !== null && onChange(next)} disabled={disabled}>
      <SegmentedControlIndicator />
      {MODES.map((mode) => (
        <SegmentedControlItem key={mode.value} value={mode.value}>
          {mode.label}
        </SegmentedControlItem>
      ))}
    </SegmentedControl>
  );
}
