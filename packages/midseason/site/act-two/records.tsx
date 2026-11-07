/**
 * The record book with the awards, the last chapter of Act II: the high, the low, the biggest margin, and the closest
 * game, then the awards as small cards, each with a headshot or a team avatar. Heartbreak and Beatdown sit on their
 * game in the book, so each game shows once.
 */
import type { ReactNode } from "react";
import { num } from "@cpc/design/format/format";
import { avatarSrc, sleeperHeadshot } from "@cpc/league/images";
import type { Avatars } from "../report/chapter-part";
import { ReportCard } from "../report/report-card";
import { ReportPhoto } from "../report/report-photo";
import { teamScore } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import type { Award, RecordsChapter } from "../schema/midseason-types";

type Book = RecordsChapter["facts"];

/* The title of an award, a mono caps word in the accent color with no box, as the awards of the R3 board. */
function AwardTitle({ award }: { award: Award }) {
  return <b className="font-mono text-meta font-bold tracking-caps text-accent-ink uppercase">{award.title}</b>;
}

/* The words of an award: "Title — winner — short fact". The short fact never names the winner, so no name repeats. */
function AwardWords({ award }: { award: Award }) {
  return (
    <>
      <AwardTitle award={award} /> —{" "}
      <b className="font-bold text-ink">{award.player !== null ? `${award.player}, ${award.team}` : award.team}</b> —{" "}
      <span>{award.short_fact}</span>
    </>
  );
}

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
        <span className="text-meta leading-normal text-ink-2">
          <AwardWords award={award} />
        </span>
      )}
    </li>
  );
}

function BookList({ book }: { book: Book }) {
  const onGame = (key: Award["key"]) => book.awards.find((award) => award.key === key && award.in_record_book);
  const { high, low, biggest_margin: big, closest } = book;
  return (
    <ReportCard className="py-sp-1">
      <ol aria-label="Records" className="m-0 list-none p-0">
        <Entry label="Highest score" value={teamScore(high.score)} line={`${high.team}, week ${high.week}`} />
        <Entry label="Lowest score" value={teamScore(low.score)} line={`${low.team}, week ${low.week}`} />
        <Entry
          label="Biggest margin"
          value={num(big.margin)}
          line={`${big.winner} ${teamScore(big.winner_score)}, ${big.loser} ${teamScore(big.loser_score)}, week ${big.week}`}
          award={onGame("beatdown")}
        />
        <Entry
          label="Closest game"
          value={num(closest.margin)}
          line={`${closest.winner} ${teamScore(closest.winner_score)}, ${closest.loser} ${teamScore(closest.loser_score)}, week ${closest.week}`}
          award={onGame("heartbreak")}
        />
      </ol>
    </ReportCard>
  );
}

/* The awards as small cards in a grid that wraps (decision ticket 15, later change): the headshot of the player for a
   player award, else the avatar of the team, then "MVP — Jahmyr Gibbs, Maye d'force B with U — short fact". */
function Awards({ awards, avatars }: { awards: Award[]; avatars: Avatars }) {
  return (
    <ul aria-label="Awards" className="m-0 grid list-none grid-cols-1 gap-sp-2 p-0 tablet:grid-cols-2 desktop:grid-cols-3">
      {awards.map((award) => (
        <ReportCard as="li" key={award.key} className="flex items-start gap-sp-3">
          <ReportPhoto
            src={award.player_id !== null ? sleeperHeadshot(award.player_id) : avatarSrc(avatars, award.roster_id)}
            name={award.player ?? award.team}
          />
          <span className="min-w-0 text-meta leading-normal text-ink-2">
            <AwardWords award={award} />
          </span>
        </ReportCard>
      ))}
    </ul>
  );
}

export function Records({ chapter, avatars }: { chapter: RecordsChapter; avatars: Avatars }) {
  const book = chapter.facts;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb}>
      <BookList book={book} />
      <h4 className="m-0 mt-sp-3 text-body leading-tight font-bold">The Awards</h4>
      <Awards awards={book.awards.filter((award) => !award.in_record_book)} avatars={avatars} />
    </ReportChapter>
  );
}
