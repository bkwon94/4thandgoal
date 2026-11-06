/**
 * Draft steals and busts, the first chapter of Act II: the top steals and the top busts of the league's own draft,
 * each with its cost rank against its points rank at the position. A bust has a tag, hurt or just bad.
 */
import { num } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { Tag } from "@cpc/design/parts/tag";
import { ReportChapter } from "../report/report-chapter";
import type { DraftChapter, DraftRow } from "../schema/midseason-types";

type DraftType = DraftChapter["facts"]["draft_type"];

/* An auction pick costs dollars, and a snake or a linear pick costs its pick number. */
const costText = (row: DraftRow, type: DraftType) => (type === "auction" ? `$${row.cost}` : `Pick ${row.cost}`);

const TAGS = { hurt: "Hurt", "just bad": "Just bad" } as const;

function Row({ row, type }: { row: DraftRow; type: DraftType }) {
  return (
    <li className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-x-sp-3 border-b border-rule py-sp-2 last:border-b-0">
      <span className="min-w-0">
        <span className="block text-body leading-tight font-bold">
          {row.name}
          {row.tag !== null && <Tag className="text-meta">{TAGS[row.tag]}</Tag>}
        </span>
        <span className="block text-meta leading-tight text-ink-2">
          {row.position} · {row.team} · {costText(row, type)}
        </span>
      </span>
      <span className="text-right">
        <span className="block font-mono text-meta text-ink-2 tabular-nums">
          {row.position}
          {row.cost_rank} cost, {row.position}
          {row.points_rank} points
        </span>
        <span className="block font-mono text-meta text-mute tabular-nums">{num(row.points)} pts</span>
      </span>
    </li>
  );
}

function List({ label, rows, type }: { label: string; rows: DraftRow[]; type: DraftType }) {
  return (
    <div className="flex flex-col gap-sp-2">
      <h4 className="m-0 text-body leading-tight font-bold">{label}</h4>
      <Card className="py-sp-1">
        <ol aria-label={label} className="m-0 list-none p-0">
          {rows.map((row) => (
            <Row key={row.player_id} row={row} type={type} />
          ))}
        </ol>
      </Card>
    </div>
  );
}

export function Draft({ chapter }: { chapter: DraftChapter }) {
  const { draft_type: type, steals, busts } = chapter.facts;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} note="Cost rank against points rank" blurb={chapter.blurb} roast={chapter.roast}>
      <div className="grid gap-sp-4 desktop:grid-cols-2">
        <List label="Steals" rows={steals} type={type} />
        <List label="Busts" rows={busts} type={type} />
      </div>
    </ReportChapter>
  );
}
