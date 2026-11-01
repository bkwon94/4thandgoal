/**
 * The War chest waiver page: the budget ring, the bucket tabs, the drift field, the sheet, and the list of the rest of the bucket.
 * It holds the open bucket and the sheet player as state, so it is a client component.
 */
"use client";

import { useEffect, useState } from "react";
import { useMarkHydrated } from "@/hooks/use-mark-hydrated";
import { avatarSrc } from "@/lib/avatar";
import { Chapter } from "@/components/parts/chapter";
import { Label } from "@/components/parts/label";
import { sleeperHeadshot, swapToDefault } from "@/lib/headshot";
import { getTeamPick, setTeamPick } from "@/lib/team-pick";
import { cn } from "@/lib/utils";
import { BEST_ADDS, BUCKETS, type BucketKey, type BudgetRow, type WaiverBoard, type WaiverPlayer } from "@/lib/waiver-types";
import type { AvatarMap, Team } from "@/lib/week-types";
import { DriftField } from "./drift-field";
import { SLOTS } from "./field-layout";
import { holderLine, priceText, teamName, waiverMetaLine } from "./format";
import { PlayerSheet } from "./player-sheet";
import { TeamPick } from "./team-pick";

/* The most money first. Two equal budgets go in waiver order, since the first claim wins a tie bid. */
function byBudget(rows: BudgetRow[]): BudgetRow[] {
  return [...rows].sort((a, b) => b.budget_left - a.budget_left || a.waiver_order - b.waiver_order);
}

/* The viewer's own drop candidates first, so a manager sees his roster before the rest. The sort is stable, so each group keeps the file rank. */
function viewerDropsFirst(players: WaiverPlayer[], viewerId: number | null): WaiverPlayer[] {
  if (viewerId === null) return players;
  const own = (player: WaiverPlayer) => (player.drop?.roster_id === viewerId ? 0 : 1);
  return [...players].sort((a, b) => own(a) - own(b));
}

/* The twelve budgets as a row of avatars over thin bars. The largest budget fills its bar, so the ring needs no league cap.
   The viewer's bar is red, so a manager finds his own budget at once. */
function BudgetRing({
  budgets,
  teams,
  avatars,
  viewerId,
}: {
  budgets: BudgetRow[];
  teams: Record<string, Team>;
  avatars: AvatarMap;
  viewerId: number | null;
}) {
  const rows = byBudget(budgets);
  const top = Math.max(1, ...rows.map((row) => row.budget_left));
  return (
    <ol aria-label="Budgets" className="m-0 grid list-none grid-cols-12 p-0">
      {rows.map((row) => (
        <li key={row.roster_id} className="flex flex-col items-center">
          <img
            src={avatarSrc(avatars, row.roster_id)}
            alt=""
            className="size-ring-avatar rounded-full border border-rule-dark bg-gry object-cover"
          />
          {/* The bar is a picture of the number under it, so it is hidden from a screen reader. */}
          <span aria-hidden className="relative mt-sp-1 block h-ring-bar w-ring-bar-w overflow-hidden rounded-sm bg-rule-dark">
            <span
              data-viewer={row.roster_id === viewerId || undefined}
              className={cn("absolute inset-x-0 bottom-0 rounded-sm", row.roster_id === viewerId ? "bg-red" : "bg-bar-off")}
              style={{ height: `${(row.budget_left / top) * 100}%` }}
            />
          </span>
          <span className="mt-sp-0 text-label text-on-dark-muted tabular-nums">{`$${row.budget_left}`}</span>
          {/* Twelve names do not fit in one row at 390, so the name is for a screen reader only. */}
          <span className="sr-only">{teamName(teams, row.roster_id)}</span>
        </li>
      ))}
    </ol>
  );
}

/* Rank, headshot, player, and price. A drop has no price, so his row names the roster that holds him. */
const ROW_GRID =
  "grid grid-cols-[var(--spacing-standings-rank)_var(--spacing-avatar)_1fr_var(--spacing-val-col)] items-center gap-sp-2 text-row leading-tight tabular-nums";

/* The players after the top six. The field holds the top six, so the list starts at rank 7. */
function RestList({
  players,
  sheetId,
  onOpen,
}: {
  players: WaiverPlayer[];
  sheetId: string | null;
  onOpen: (player: WaiverPlayer) => void;
}) {
  const rest = players.slice(SLOTS.length);
  if (rest.length === 0) return null;
  return (
    <div className="mt-sp-4">
      <Label dark className="mb-sp-1">
        Also
      </Label>
      <ol aria-label="Also" className="m-0 list-none p-0">
        {rest.map((player, index) => {
          const open = player.player_id === sheetId;
          return (
            <li key={player.player_id} className="border-b border-rule-dark">
              {/* The whole row is the button, so the touch target is the row. 44px is the smallest comfortable touch target. */}
              <button
                type="button"
                aria-pressed={open}
                onClick={() => onOpen(player)}
                className={cn(
                  ROW_GRID,
                  "press min-h-touch w-full cursor-pointer border-0 bg-transparent px-0 py-sp-1 text-left text-inherit [-webkit-tap-highlight-color:transparent]",
                )}
              >
                <span className={open ? "font-bold text-red-lt" : "text-on-dark-muted"}>{SLOTS.length + index + 1}</span>
                {/* The player name sits next to the headshot, so the image is decorative. */}
                {/* The fill is the dark rule, so it stays one step off the black card in both themes. Ink-2 turns light grey in the dark theme. */}
                <img
                  src={sleeperHeadshot(player.player_id)}
                  alt=""
                  loading="lazy"
                  onError={swapToDefault}
                  className="size-avatar rounded-full bg-rule-dark object-cover object-top"
                />
                <span className="flex min-w-0 flex-col">
                  <b className="font-extrabold">{player.name}</b>
                  <span className="text-meta text-on-dark-muted">
                    {player.drop ? `${waiverMetaLine(player)} · ${holderLine(player.drop)}` : waiverMetaLine(player)}
                  </span>
                </span>
                <span className="text-right font-bold">{priceText(player)}</span>
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

export function WarChest({ board, teams, avatars }: { board: WaiverBoard; teams: Record<string, Team>; avatars: AvatarMap }) {
  // Only the buckets in the file get a tab, so an older file shows no empty tabs.
  const tabs = BUCKETS.filter(({ key }) => board.buckets[key]);
  const [bucket, setBucket] = useState<BucketKey>(BEST_ADDS);
  // The sheet holds the player and not an index, so it keeps him when the tab changes to a bucket without him.
  const [sheetPlayer, setSheetPlayer] = useState<WaiverPlayer | null>(board.buckets[BEST_ADDS]?.[0] ?? null);
  const sheetId = sheetPlayer?.player_id ?? null;
  // Undefined until the page reads storage after the first render, since the static page has no storage. Null is no pick.
  const [pick, setPick] = useState<number | null | undefined>(undefined);
  // A roster id that the budget table does not hold, such as a stale pick after a league change, counts as no pick.
  const viewer = board.budgets.find((row) => row.roster_id === pick) ?? null;
  const players = viewerDropsFirst(board.buckets[bucket] ?? [], viewer?.roster_id ?? null);
  useMarkHydrated();

  useEffect(() => {
    setPick(getTeamPick());
  }, []);

  function choose(rosterId: number) {
    setPick(rosterId);
    setTeamPick(rosterId);
  }

  return (
    <Chapter dark>
      <div className="mb-sp-4">
        {/* Before the read, an empty slot of the chip height holds the place. A returning manager never sees the list flash open,
            and the ring does not move down when his chip shows. */}
        {pick === undefined ? (
          <div aria-hidden className="h-pick-chip" />
        ) : (
          <TeamPick viewer={viewer} budgets={board.budgets} teams={teams} avatars={avatars} onPick={choose} />
        )}
      </div>
      <Label dark>War chest</Label>
      <BudgetRing budgets={board.budgets} teams={teams} avatars={avatars} viewerId={viewer?.roster_id ?? null} />
      <div role="group" aria-label="Buckets" className="mt-sp-4 flex gap-sp-1">
        {tabs.map((tab) => {
          const on = tab.key === bucket;
          return (
            <button
              key={tab.key}
              type="button"
              aria-pressed={on}
              onClick={() => setBucket(tab.key)}
              className={cn(
                "press flex min-h-touch flex-1 cursor-pointer items-center justify-center rounded-full border-0 px-sp-2 text-label font-bold tracking-caps whitespace-nowrap uppercase",
                on ? "bg-red text-on-dark" : "bg-chip-dark text-on-dark-2",
              )}
            >
              {tab.name}
            </button>
          );
        })}
      </div>
      <div className="mt-sp-3">
        <DriftField bucket={bucket} players={players} openId={sheetId} onOpen={setSheetPlayer} />
      </div>
      <PlayerSheet
        player={sheetPlayer}
        teams={teams}
        expertsMissing={board.experts_missing === true}
        viewerBudget={viewer?.budget_left ?? null}
      />
      <RestList players={players} sheetId={sheetId} onOpen={setSheetPlayer} />
    </Chapter>
  );
}
