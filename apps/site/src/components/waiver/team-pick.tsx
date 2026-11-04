/**
 * The team pick of the waiver page: the analyzer's team list with no pick, and a chip with the team and its budget after a pick.
 * The War chest owns the pick, so the ring, the sheet, and the drops read the same roster id.
 */
"use client";

import { useEffect, useRef, useState } from "react";
import { TeamPicker } from "@/components/analyzer/team-picker";
import { Avatar } from "@cpc/league/avatar";
import { avatarSrc } from "@cpc/league/images";
import type { Team as PickerTeam } from "@/lib/api";
import type { BudgetRow } from "@/lib/waiver-types";
import type { AvatarMap, Team } from "@/lib/week-types";
import { teamName } from "./format";

const LABEL = "Your team";

/* The picker wants the analyzer's team shape. The waiver page has no rosters to show, so each team has no players. */
function pickerTeams(budgets: BudgetRow[], teams: Record<string, Team>, avatars: AvatarMap): PickerTeam[] {
  return [...budgets]
    .sort((a, b) => a.roster_id - b.roster_id)
    .map((row) => ({
      roster_id: row.roster_id,
      team: teamName(teams, row.roster_id),
      manager: teams[String(row.roster_id)]?.owner ?? "",
      avatar: avatarSrc(avatars, row.roster_id),
      players: [],
    }));
}

/* The picked team as one row: the avatar, the name, the budget left, and a Change link that opens the list again.
   The picker has its own collapsed row, but it opens on every mount and has no budget line. A change to it changes the analyzer,
   so the waiver page keeps this second chip. */
function PickChip({ name, avatar, budget, onChange }: { name: string; avatar: string; budget: number; onChange: () => void }) {
  return (
    <section aria-label={LABEL} className="flex h-pick-chip items-center gap-sp-3 rounded-card bg-chip-dark py-sp-1 pl-sp-3">
      <Avatar src={avatar} />
      <span className="flex min-w-0 flex-1 flex-col">
        <b className="truncate text-row leading-tight font-extrabold">{name}</b>
        <span className="text-meta text-on-dark-muted tabular-nums">{`you have $${budget}`}</span>
      </span>
      <button
        type="button"
        onClick={onChange}
        aria-label={`Change ${LABEL.toLowerCase()}`}
        className="press min-h-touch flex-none cursor-pointer rounded-card border-0 bg-transparent px-sp-4 text-label font-bold tracking-wide text-on-dark uppercase underline underline-offset-4"
      >
        Change
      </button>
    </section>
  );
}

export function TeamPick({
  viewer,
  budgets,
  teams,
  avatars,
  onPick,
}: {
  viewer: BudgetRow | null;
  budgets: BudgetRow[];
  teams: Record<string, Team>;
  avatars: AvatarMap;
  onPick: (rosterId: number) => void;
}) {
  const [changing, setChanging] = useState(false);
  const list = useRef<HTMLDivElement>(null);
  // The Change link leaves the page when the list opens, so focus moves to the picked radio and not to the body.
  const focusAfterOpen = useRef(false);

  useEffect(() => {
    if (!changing || !focusAfterOpen.current) return;
    focusAfterOpen.current = false;
    list.current?.querySelector<HTMLInputElement>("input:checked")?.focus();
  }, [changing]);

  if (viewer && !changing) {
    return (
      <PickChip
        name={teamName(teams, viewer.roster_id)}
        avatar={avatarSrc(avatars, viewer.roster_id)}
        budget={viewer.budget_left}
        onChange={() => {
          focusAfterOpen.current = true;
          setChanging(true);
        }}
      />
    );
  }
  return (
    <div ref={list}>
      <TeamPicker
        label={LABEL}
        teams={pickerTeams(budgets, teams, avatars)}
        value={viewer?.roster_id ?? null}
        disabledId={null}
        onChange={(rosterId) => {
          setChanging(false);
          onPick(rosterId);
        }}
      />
    </div>
  );
}
