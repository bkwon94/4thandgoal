/**
 * Players to watch, a chapter of Act III: Due to rise and Due to fall from the Expected gap a game, and Grab him now
 * from the projections of the weeks left. Each list holds 3 players.
 */
import type { ReactNode } from "react";
import { oneDecimal } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { Tag } from "@cpc/design/parts/tag";
import { ReportChapter } from "../report/report-chapter";
import type { GapPlayer, GrabPlayer, WatchChapter } from "../schema/midseason-types";

const ROW = "grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0";

function Who({ name, position, nfl_team }: { name: string; position: string; nfl_team: string | null }) {
  return (
    <>
      <span className="block text-body leading-tight font-bold">{name}</span>
      <span className="block text-meta leading-tight text-ink-2">
        {position} · {nfl_team ?? "No team"}
      </span>
    </>
  );
}

/* A gap under zero is a player under his expected points, so he is due to rise. */
function GapRow({ player }: { player: GapPlayer }) {
  return (
    <li className={ROW}>
      <span className="min-w-0">
        <Who {...player} />
        <span className="block text-meta leading-tight text-ink-2">{player.manager}</span>
      </span>
      <span className="text-right font-mono text-meta text-ink-2 tabular-nums">
        <span className="block text-body font-bold text-ink">{oneDecimal(Math.abs(player.gap))}</span> a game {player.gap < 0 ? "under" : "over"}
      </span>
    </li>
  );
}

function GrabRow({ player }: { player: GrabPlayer }) {
  return (
    <li className={ROW}>
      <span className="min-w-0">
        <Who {...player} />
        <Tag className="ml-0 text-meta">Free agent</Tag>
      </span>
      <span className="text-right font-mono text-meta text-ink-2 tabular-nums">
        <span className="block text-body font-bold text-ink">{Math.round(player.projection)}</span> projected
      </span>
    </li>
  );
}

function List({ label, note, children }: { label: string; note: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-sp-2">
      <h4 className="m-0 text-body leading-tight font-bold">{label}</h4>
      <span className="text-meta leading-tight text-ink-2">{note}</span>
      <Card className="py-sp-1">
        <ol aria-label={label} className="m-0 list-none p-0">
          {children}
        </ol>
      </Card>
    </div>
  );
}

export function Watch({ chapter }: { chapter: WatchChapter }) {
  const { due_to_rise: rise, due_to_fall: fall, grab_him_now: grab } = chapter.facts;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb}>
      <div className="grid gap-sp-4 desktop:grid-cols-3">
        <List label="Due to Rise" note="Points a game under his expected points.">
          {rise.map((player) => <GapRow key={player.player_id} player={player} />)}
        </List>
        <List label="Due to Fall" note="Points a game over his expected points.">
          {fall.map((player) => <GapRow key={player.player_id} player={player} />)}
        </List>
        <List label="Grab Him Now" note="Projected points for the weeks left.">
          {grab.map((player) => <GrabRow key={player.player_id} player={player} />)}
        </List>
      </div>
    </ReportChapter>
  );
}
