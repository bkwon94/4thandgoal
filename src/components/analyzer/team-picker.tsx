/**
 * A labelled list of teams as a radio group. Each row shows the avatar, the team name, and the manager.
 * The parent owns the choice, so two pickers can disable each other's pick. A pick collapses the list to that row.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useRef, useState } from "react";
import type { Team } from "@/lib/api";
import { AVATAR_FALLBACK, swapAvatarToDefault } from "@/lib/avatar";
import { DURATION, EASE_OUT, INSTANT, useMotionOff } from "@/lib/motion";
import { cn } from "@/lib/utils";

type TeamPickerProps = {
  // Also the name of the radio group, so two pickers on one page stay apart.
  label: string;
  teams: Team[];
  value: number | null;
  // The roster id that the other picker holds. This picker shows that row as disabled.
  disabledId: number | null;
  onChange: (rosterId: number) => void;
  // A grade runs, so every row and the Change button stay off until the grade ends.
  locked?: boolean;
};

export function TeamPicker({ label, teams, value, disabledId, onChange, locked = false }: TeamPickerProps) {
  // The list opens until a pick, then it collapses to the chosen row, so the form fits on a phone screen.
  const [open, setOpen] = useState(true);
  const off = useMotionOff();
  const fieldset = useRef<HTMLFieldSetElement>(null);
  // The Change button leaves the page when the list opens, so focus moves to the chosen radio instead of the body.
  const focusAfterOpen = useRef(false);
  const collapsed = value !== null && !open;
  const shown = collapsed ? teams.filter((team) => team.roster_id === value) : teams;

  useEffect(() => {
    if (!open || !focusAfterOpen.current) return;
    focusAfterOpen.current = false;
    fieldset.current?.querySelector<HTMLInputElement>("input:checked")?.focus();
  }, [open]);

  function pick(rosterId: number) {
    setOpen(false);
    onChange(rosterId);
  }

  function reopen() {
    focusAfterOpen.current = true;
    setOpen(true);
  }

  const rows = shown.map((team) => {
    const disabled = locked || team.roster_id === disabledId;
    return (
      <motion.div
        key={team.roster_id}
        initial={off ? false : { height: 0, opacity: 0 }}
        animate={{ height: "auto", opacity: 1 }}
        exit={{ height: 0, opacity: 0 }}
        transition={off ? INSTANT : { duration: DURATION.collapse, ease: EASE_OUT }}
        className="overflow-hidden"
      >
        {/* The gap lives inside the animated box, so a closing row takes its gap with it and nothing jumps at the end. */}
        <div className="pb-sp-1">
          <div
            className={cn(
              "group flex min-h-touch items-center rounded-card bg-gry has-checked:bg-card-blk has-checked:text-on-dark has-[input:focus-visible]:outline-2 has-[input:focus-visible]:outline-offset-2 has-[input:focus-visible]:outline-red",
              disabled && "opacity-40",
            )}
          >
            <label
              aria-disabled={disabled || undefined}
              className={cn(
                "flex min-h-touch min-w-0 flex-1 cursor-pointer items-center gap-sp-3 px-sp-3 py-sp-1",
                disabled ? "cursor-not-allowed" : "press",
              )}
            >
              {/* The input is visually hidden, and the row shows the choice. The input stays in the page for the keyboard and for screen readers. */}
              <input
                type="radio"
                name={label}
                value={team.roster_id}
                checked={value === team.roster_id}
                disabled={disabled}
                onChange={() => pick(team.roster_id)}
                className="sr-only"
              />
              <img
                src={team.avatar ?? AVATAR_FALLBACK}
                alt=""
                onError={swapAvatarToDefault}
                className="size-avatar flex-none rounded-full bg-wht object-cover"
              />
              <span className="flex min-w-0 flex-col">
                <b className="text-row leading-tight font-extrabold">{team.team}</b>
                <span className="text-meta text-mute group-has-checked:text-on-dark-muted">{team.manager}</span>
              </span>
            </label>
            {collapsed && (
              <button
                type="button"
                onClick={reopen}
                disabled={locked}
                aria-label={`Change ${label.toLowerCase()}`}
                className="press min-h-touch flex-none cursor-pointer rounded-card disabled:cursor-not-allowed px-sp-4 text-label font-bold tracking-wide text-on-dark uppercase underline underline-offset-4"
              >
                Change
              </button>
            )}
          </div>
        </div>
      </motion.div>
    );
  });

  return (
    <fieldset ref={fieldset} className="m-0 min-w-0 border-0 p-0">
      <legend className="mb-sp-2 p-0 text-label font-bold tracking-wide text-red-ink uppercase">{label}</legend>
      <div className="flex flex-col">
        {/* With motion off, the rows switch at once, with no exit to wait for. initial={false}: the full list shows at once on load. */}
        {off ? rows : <AnimatePresence initial={false}>{rows}</AnimatePresence>}
      </div>
    </fieldset>
  );
}
