/**
 * The record book with the awards, the last chapter of Act II: the high, the low, the biggest margin, and the closest
 * game, then the awards. Heartbreak and Beatdown sit on their game in the book, so each game shows once.
 */
import type { ReactNode } from "react";
import { num } from "@cpc/design/format/format";
import { Card } from "@cpc/design/parts/card";
import { Tag } from "@cpc/design/parts/tag";
import { ReportChapter } from "../report/report-chapter";
import type { Award, RecordsChapter } from "../schema/midseason-types";

type Book = RecordsChapter["facts"];

/* One record: its label, the team and the number, the line under it, and the award of its game when it has one. */
function Entry({ label, value, line, award }: { label: string; value: string; line: ReactNode; award?: Award }) {
  return (
    <li className="flex flex-col gap-sp-1 border-b border-rule py-sp-3 last:border-b-0">
      <span className="flex flex-wrap items-baseline justify-between gap-x-sp-3">
        <span className="font-mono text-meta font-bold tracking-caps text-mute uppercase">{label}</span>
        <span className="font-mono text-stat leading-tight font-bold tabular-nums">{value}</span>
      </span>
      <span className="text-body leading-tight">{line}</span>
      {award !== undefined && (
        <span className="text-meta leading-tight text-ink-2">
          <Tag className="ml-0 text-meta">{award.title}</Tag> {award.fact}
        </span>
      )}
    </li>
  );
}

function BookList({ book }: { book: Book }) {
  const onGame = (key: Award["key"]) => book.awards.find((award) => award.key === key && award.in_record_book);
  const { high, low, biggest_margin: big, closest } = book;
  return (
    <Card className="py-sp-1">
      <ol aria-label="Records" className="m-0 list-none p-0">
        <Entry label="Highest score" value={num(high.score)} line={`${high.team}, week ${high.week}`} />
        <Entry label="Lowest score" value={num(low.score)} line={`${low.team}, week ${low.week}`} />
        <Entry
          label="Biggest margin"
          value={num(big.margin)}
          line={`${big.winner} ${num(big.winner_score)}, ${big.loser} ${num(big.loser_score)}, week ${big.week}`}
          award={onGame("beatdown")}
        />
        <Entry
          label="Closest game"
          value={num(closest.margin)}
          line={`${closest.winner} ${num(closest.winner_score)}, ${closest.loser} ${num(closest.loser_score)}, week ${closest.week}`}
          award={onGame("heartbreak")}
        />
      </ol>
    </Card>
  );
}

function Awards({ awards }: { awards: Award[] }) {
  return (
    <ul aria-label="Awards" className="m-0 grid list-none gap-sp-3 p-0 tablet:grid-cols-2">
      {awards.map((award) => (
        <Card key={award.key} as="li" className="flex flex-col gap-sp-1">
          <h5 className="m-0 font-mono text-meta font-bold tracking-caps text-accent-ink uppercase">{award.title}</h5>
          <span className="text-body leading-tight font-bold">{award.player ?? award.team}</span>
          <span className="text-meta leading-tight text-ink-2">{award.fact}</span>
        </Card>
      ))}
    </ul>
  );
}

export function Records({ chapter }: { chapter: RecordsChapter }) {
  const book = chapter.facts;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb} roast={chapter.roast}>
      <BookList book={book} />
      <h4 className="m-0 mt-sp-3 text-body leading-tight font-bold">The awards</h4>
      <Awards awards={book.awards.filter((award) => !award.in_record_book)} />
    </ReportChapter>
  );
}
