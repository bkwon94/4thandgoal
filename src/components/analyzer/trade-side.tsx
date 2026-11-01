/**
 * One side of the trade form: the heading, the team and player pickers, and a row per picked player with its To picker.
 * The form owns the sides, so this part only reads its side and reports each change.
 */
"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useId } from "react";
import { XIcon } from "lucide-react";
import type { PlayerPick } from "@/components/analyzer/trade-form";
import { Avatar } from "@/components/parts/avatar";
import { Headshot } from "@/components/parts/headshot";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import type { Team, TeamPlayer } from "@/lib/api";
import { AVATAR_FALLBACK } from "@/lib/avatar";
import { count } from "@/lib/format/format";
import { HEADSHOT_FALLBACK } from "@/lib/headshot";
import { useMotionOff } from "@/hooks/use-motion-off";
import { enterExit } from "@/lib/motion";
import { cn } from "@/lib/utils";

type TradeSideProps = {
  // The heading of the side, such as "Your Team". It also names the team picker.
  title: string;
  // The teams this side can pick: every team that no other side holds.
  teams: Team[];
  // The picked team of this side, or undefined before a pick.
  team: Team | undefined;
  // The players this side gives, in the order of the pick, each with the id of its destination side.
  picks: PlayerPick[];
  // The other sides a player can go to, or null at two sides, where the destination is the other side and no To picker shows.
  destinations: SideChoice[] | null;
  onPickTeam: (rosterId: number) => void;
  onPickPlayers: (playerIds: string[]) => void;
  onPickDestination: (playerId: string, toSide: number) => void;
  // Set only for the third and fourth sides. The heading then shows a remove control.
  onRemove?: () => void;
  // A grade runs, so no picker or remove control may change the trade that the grade reads.
  locked: boolean;
};

/* Another side of the trade, by its id, with its team once picked. */
type SideChoice = { id: number; team: Team | undefined };

/* The trigger of both pickers: a grey row as tall as a touch target, with a hover fill and a red focus ring. */
const TRIGGER =
  "press w-full min-w-0 justify-start gap-sp-3 rounded-card border-0 bg-gry px-sp-3 py-sp-1 text-left text-row text-ink data-[size=default]:h-auto min-h-touch hover:bg-rule focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red focus-visible:ring-0 disabled:opacity-40 [&>[data-slot=select-value]]:min-w-0 [&>[data-slot=select-value]]:flex-1";

/* An item of a picker popup: a touch-tall row that fills on hover and on keyboard focus. */
const ITEM = "min-h-touch gap-sp-3 rounded-sm px-sp-2 pr-sp-6 text-row text-ink data-highlighted:bg-gry focus:bg-gry";

/* The label above a picker: small red caps, as the form used for its legends. The text stays in title case for a screen reader. */
const LABEL = "m-0 text-label font-bold tracking-wide text-red-ink uppercase";

/* A round image in a picker. The faint ring gives the image an edge on the grey row in both themes. The size prop of each part sets the size. */
const ROUND_IMG = "flex-none rounded-full bg-wht object-cover ring-1 ring-ink/10";

function TeamAvatar({ team }: { team: Team }) {
  return <Avatar src={team.avatar ?? AVATAR_FALLBACK} className={ROUND_IMG} />;
}

function PlayerHeadshot({ player }: { player: TeamPlayer }) {
  return <Headshot src={player.headshot || HEADSHOT_FALLBACK} size="avatar" lazy className={cn(ROUND_IMG, "object-top")} />;
}

/* The name over the position and the NFL team. min-w-0 lets a long name truncate and not push the row wider. */
function PlayerText({ player }: { player: TeamPlayer }) {
  return (
    <span className="flex min-w-0 flex-col">
      <b className="truncate text-row leading-tight font-extrabold">{player.name}</b>
      <span className="text-meta text-mute">
        {player.position} {player.nfl_team}
      </span>
    </span>
  );
}

/* The trigger text of the player picker: the count once the side gives a player. */
function countText(n: number): string {
  if (n === 0) return "Pick Players";
  return count(n, "Player", "Players");
}

/* The small To picker of a picked row. It sits in the meta line, so the row reads "Name", then "WR NYJ · To <Team>". */
function DestinationPicker({
  value,
  destinations,
  onPick,
  locked,
}: {
  value: number;
  destinations: SideChoice[];
  onPick: (to: number) => void;
  locked: boolean;
}) {
  const labelId = useId();
  const current = destinations.find((d) => d.id === value);
  return (
    <span className="flex min-w-0 items-center gap-sp-1">
      <span aria-hidden="true">·</span>
      <span id={labelId}>To</span>
      <Select<number>
        value={value}
        onValueChange={(to) => {
          if (to !== null) onPick(to);
        }}
        disabled={locked}
      >
        {/* The trigger is short to fit the meta line. The negative margin and the padding give it a taller hit area. */}
        <SelectTrigger
          aria-labelledby={labelId}
          className="press -my-sp-1 h-auto min-w-0 gap-sp-1 rounded-sm border-0 bg-transparent px-sp-1 py-sp-1 text-meta font-bold text-red-ink underline decoration-red-ink/50 underline-offset-2 hover:bg-red/10 focus-visible:outline-2 focus-visible:outline-red focus-visible:ring-0 disabled:opacity-40 data-[size=default]:h-auto [&>[data-slot=select-value]]:min-w-0 [&_svg]:text-red-ink"
        >
          <SelectValue>{() => <span className="truncate">{current?.team?.team ?? "Pick a Team"}</span>}</SelectValue>
        </SelectTrigger>
        {/* The trigger is narrow, so the popup takes the width of its longest team, capped by the room on the screen. */}
        <SelectContent
          alignItemWithTrigger={false}
          align="start"
          className="w-max max-w-[min(20rem,var(--available-width))] min-w-48 p-sp-1 motion-reduce:animate-none"
        >
          {destinations.map((d) => (
            <SelectItem key={d.id} value={d.id} className={ITEM}>
              {d.team && <TeamAvatar team={d.team} />}
              <b className="min-w-0 truncate leading-tight font-extrabold">{d.team?.team ?? "Pick a Team"}</b>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </span>
  );
}

export function TradeSide({
  title,
  teams,
  team,
  picks,
  destinations,
  onPickTeam,
  onPickPlayers,
  onPickDestination,
  onRemove,
  locked,
}: TradeSideProps) {
  const headingId = useId();
  const playersLabelId = useId();
  const off = useMotionOff();
  const ids = picks.map((p) => p.playerId);
  const picked = team
    ? picks.flatMap((pick) => {
        const player = team.players.find((p) => p.player_id === pick.playerId);
        return player ? [{ player, toSide: pick.toSide }] : [];
      })
    : [];

  return (
    <div role="group" aria-labelledby={headingId} className="flex min-w-0 flex-col gap-sp-3">
      <div className="flex min-h-sp-5 items-center justify-between gap-sp-2">
        <h3 id={headingId} className={LABEL}>
          {title}
        </h3>
        {onRemove && (
          // The control is as tall as the heading line, and the negative margin gives it a touch-size hit area.
          <button
            type="button"
            aria-label={`Remove ${title}`}
            disabled={locked}
            onClick={onRemove}
            className="press -my-sp-3 -mr-sp-2 grid size-touch flex-none cursor-pointer place-items-center rounded-card text-mute hover:text-ink focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-red disabled:cursor-not-allowed disabled:opacity-40"
          >
            <XIcon aria-hidden="true" className="size-4" />
          </button>
        )}
      </div>
      <Select<number>
        value={team?.roster_id ?? null}
        onValueChange={(rosterId) => {
          if (rosterId !== null) onPickTeam(rosterId);
        }}
        disabled={locked}
      >
        <SelectTrigger aria-labelledby={headingId} className={TRIGGER}>
          <SelectValue>
            {() =>
              team ? (
                <span className="flex min-w-0 items-center gap-sp-3">
                  <TeamAvatar team={team} />
                  <b className="truncate text-row leading-tight font-extrabold">{team.team}</b>
                </span>
              ) : (
                <span className="text-mute">Pick a Team</span>
              )
            }
          </SelectValue>
        </SelectTrigger>
        <SelectContent alignItemWithTrigger={false} className="p-sp-1 motion-reduce:animate-none">
          {teams.map((t) => (
            <SelectItem key={t.roster_id} value={t.roster_id} className={ITEM}>
              <TeamAvatar team={t} />
              <span className="flex min-w-0 flex-col">
                <b className="truncate leading-tight font-extrabold">{t.team}</b>
                <span className="text-meta text-mute">{t.manager}</span>
              </span>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {team && (
        <div className="flex min-w-0 flex-col gap-sp-2">
          <span id={playersLabelId} className={LABEL}>
            {`${team.team} Gives`}
          </span>
          <Select<string, true> multiple value={ids} onValueChange={(next) => onPickPlayers(next)} disabled={locked}>
            <SelectTrigger aria-labelledby={playersLabelId} className={TRIGGER}>
              <SelectValue>
                {(ids: string[]) => (
                  <span className={cn("tabular-nums", ids.length === 0 && "text-mute")}>{countText(ids.length)}</span>
                )}
              </SelectValue>
            </SelectTrigger>
            <SelectContent alignItemWithTrigger={false} className="p-sp-1 motion-reduce:animate-none">
              {team.players.map((player) => (
                <SelectItem key={player.player_id} value={player.player_id} className={ITEM}>
                  <PlayerHeadshot player={player} />
                  <PlayerText player={player} />
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {/* The list stays in the page while a team is picked, so the last row can animate out. empty:hidden drops the empty
              list from the layout and from the accessibility tree. relative holds a removed row that popLayout lifts out. */}
          <ul aria-label={`Players ${team.team} Gives`} className="relative m-0 flex list-none flex-col gap-sp-1 p-0 empty:hidden">
            <AnimatePresence initial={false} mode="popLayout">
              {picked.map(({ player, toSide }) => (
                <motion.li
                  key={player.player_id}
                  layout={!off}
                  // A picked row enters and leaves as a side does.
                  {...enterExit(off)}
                  className="flex min-h-touch w-full items-center gap-sp-3 rounded-card bg-pick py-sp-1 pl-sp-3 text-ink shadow-[inset_3px_0_0_var(--color-red)]"
                >
                  <PlayerHeadshot player={player} />
                  <span className="flex min-w-0 flex-1 flex-col">
                    <b className="truncate text-row leading-tight font-extrabold">{player.name}</b>
                    <span className="flex min-w-0 items-center gap-sp-1 text-meta whitespace-nowrap text-mute">
                      <span className="flex-none">
                        {player.position} {player.nfl_team}
                      </span>
                      {destinations && (
                        <DestinationPicker
                          value={toSide}
                          destinations={destinations}
                          onPick={(next) => onPickDestination(player.player_id, next)}
                          locked={locked}
                        />
                      )}
                    </span>
                  </span>
                  <button
                    type="button"
                    aria-label={`Remove ${player.name}`}
                    disabled={locked}
                    onClick={() => onPickPlayers(ids.filter((id) => id !== player.player_id))}
                    className="press grid size-touch flex-none cursor-pointer place-items-center rounded-card text-mute hover:text-red-ink focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-red disabled:cursor-not-allowed disabled:opacity-40"
                  >
                    <XIcon aria-hidden="true" className="size-4" />
                  </button>
                </motion.li>
              ))}
            </AnimatePresence>
          </ul>
        </div>
      )}
    </div>
  );
}
