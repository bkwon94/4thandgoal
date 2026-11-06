/**
 * Schedule luck with the Schedule swap, a chapter of Act I: a card that works one real example, the luck table with a
 * word under each luck number, then the swap as one text row per team with its best and its worst schedule.
 */
import { gap, num } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "../report/report-card";
import { fullRecord, signedTwo, teamScore } from "../report/numbers";
import { ReportChapter } from "../report/report-chapter";
import { WordTag } from "../report/word-tag";
import type { BestAndWorst, LuckChapter, LuckExample, SwapEnd, TeamLuck } from "../schema/midseason-types";

/* The label of the All-play wins. The page never says "All-play", because readers do not know the term (decision ticket 16). */
const EVERYONE = "Wins if you played everyone";

/* A gap smaller than this many wins reads "even". */
const EVEN_GAP = 0.5;
/* At this gap or more, either way, the word of the luck takes the accent color, the lines of decision ticket 06. */
const LOUD_GAP = 1.5;

const luckWord = (luck: number) => (Math.abs(luck) < EVEN_GAP ? "even" : luck > 0 ? "lucky" : "unlucky");

const HEAD = "px-sp-2 py-sp-2 text-left font-mono text-meta font-bold tracking-caps text-mute uppercase";
const CELL = "px-sp-2 py-sp-2 font-mono text-body tabular-nums whitespace-nowrap";

/* The team column stays in place while a phone scrolls the luck table, so each row keeps its name. A long name wraps on a phone. */
const LUCK_TEAM = "sticky left-0 z-10 max-w-[9rem] bg-card md:max-w-none px-sp-2 py-sp-2 text-left text-body leading-tight font-semibold";

const closeText = (team: TeamLuck) => fullRecord(team.close_wins, team.close_losses, team.close_ties);

/* A count with a half, such as 9 or 8.5 teams outscored. */
const half = (x: number) => (Number.isInteger(x) ? String(x) : x.toFixed(1));

/* The card above the luck table: the idea in plain words, then one real team worked through, then the gap. */
function LuckCard({ example, weeks }: { example: LuckExample; weeks: number }) {
  const more = example.schedule_luck >= 0 ? "more" : "fewer";
  const steps = [
    {
      title: `What "${EVERYONE.toLowerCase()}" means`,
      text: `Each week, count the ${example.others} other teams you outscored, as if you played them all that week.`,
    },
    {
      title: "One real example",
      text:
        `In week ${example.week}, ${example.name} scored ${teamScore(example.score)} and outscored ` +
        `${half(example.outscored)} of ${example.others} teams: ${example.week_wins.toFixed(2)} of a win. ` +
        `Over ${weeks} weeks it outscored ${half(example.season_outscored)} of ` +
        `${example.season_games}: ${example.all_play_wins.toFixed(2)} wins.`,
    },
    {
      title: "Luck",
      text:
        `It won ${num(example.head_to_head_wins)} real games, ${Math.abs(example.schedule_luck).toFixed(2)} ${more} ` +
        `than ${example.all_play_wins.toFixed(2)}. That gap is schedule luck.`,
    },
  ];
  return (
    <Card>
      <section aria-labelledby="luck-card-0" className="flex flex-col gap-sp-3 p-sp-4">
        {steps.map((step, index) => (
          <div key={step.title} className="flex gap-sp-3">
            <span aria-hidden className="font-mono text-meta font-bold text-mute tabular-nums">
              {index + 1}
            </span>
            <div className="flex flex-col gap-sp-1">
              <h5 id={`luck-card-${index}`} className="m-0 text-body leading-tight font-bold">
                {step.title}
              </h5>
              <p className="m-0 max-w-measure text-body text-ink-2">{step.text}</p>
            </div>
          </div>
        ))}
      </section>
    </Card>
  );
}

function LuckTable({ teams }: { teams: TeamLuck[] }) {
  return (
    <Card className="overflow-x-auto p-0">
      <table aria-label="Schedule luck" className="w-full border-collapse">
        <thead>
          <tr className="border-b border-rule">
            <th scope="col" className={cn(HEAD, "sticky left-0 z-10 bg-card")}>Team</th>
            <th scope="col" className={cn(HEAD, "text-right")}>Real wins</th>
            <th scope="col" className={cn(HEAD, "text-right")}>{EVERYONE}</th>
            <th scope="col" className={cn(HEAD, "text-right")}>Luck (gap)</th>
            <th scope="col" className={cn(HEAD, "text-right")}>PA</th>
            <th scope="col" className={cn(HEAD, "text-right")}>Close</th>
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr key={team.roster_id} className="border-b border-rule last:border-b-0">
              <th scope="row" className={LUCK_TEAM}>
                {team.name}
              </th>
              <td className={cn(CELL, "text-right")}>{num(team.head_to_head_wins)}</td>
              <td className={cn(CELL, "text-right")}>{team.all_play_wins.toFixed(2)}</td>
              <td data-luck className={cn(CELL, "text-right font-bold")}>
                <span className="block">{signedTwo(team.schedule_luck)}</span>
                {/* The word sits under the number. */}
                <WordTag tone={Math.abs(team.schedule_luck) >= LOUD_GAP ? "accent" : "mute"} className="ml-0 block">
                  {luckWord(team.schedule_luck)}
                </WordTag>
              </td>
              <td className={cn(CELL, "text-right text-ink-2")}>
                {Math.round(team.points_against)} <span className="text-meta text-mute">#{team.points_against_rank}</span>
              </td>
              <td className={cn(CELL, "text-right")}>{closeText(team)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}

/* The schedules of a best or a worst: one name, "A or B" for 2, and "A and N others" for more. */
function scheduleNames(end: SwapEnd, names: Map<number, string>) {
  const [first, ...rest] = end.schedules.map((rid) => names.get(rid) ?? "");
  if (rest.length === 0) return first;
  if (rest.length === 1) return `${first} or ${rest[0]}`;
  return `${first} and ${rest.length} others`;
}

/* The change in wins from the real record, as a muted word: "+5", "−1", or "same". */
const change = (end: SwapEnd) => (end.change === 0 ? "same" : gap(end.change));

const LABEL = "font-mono text-label font-bold tracking-caps text-mute uppercase";

function SwapEndLine({ label, end, names }: { label: string; end: SwapEnd; names: Map<number, string> }) {
  return (
    <p className="m-0 text-body leading-tight">
      <span className={LABEL}>{label}</span>{" "}
      <span className="font-mono font-bold tabular-nums">{fullRecord(end.wins, end.losses, end.ties)}</span>
      <span className="text-ink-2"> on the schedule of {scheduleNames(end, names)}</span>
      <span className="ml-sp-2 font-mono text-meta text-mute tabular-nums">{change(end)}</span>
    </p>
  );
}

/* The swap as one text row per team, sorted by the spread between best and worst. No grid and no bar (decision ticket 16). */
function SwapRows({ rows }: { rows: BestAndWorst[] }) {
  const names = new Map(rows.map((row) => [row.roster_id, row.name]));
  return (
    <ul aria-label="Schedule swap" className="m-0 flex list-none flex-col p-0">
      {rows.map((row) => (
        <li key={row.roster_id} className="flex flex-col gap-sp-1 border-b border-rule py-sp-3 last:border-b-0">
          <h5 className="m-0 text-body leading-tight font-semibold">{row.name}</h5>
          <p className="m-0 text-body leading-tight">
            <span className={LABEL}>Real</span>{" "}
            <span className="font-mono font-bold tabular-nums">{fullRecord(row.real.wins, row.real.losses, row.real.ties)}</span>
          </p>
          <SwapEndLine label="Best" end={row.best} names={names} />
          <SwapEndLine label="Worst" end={row.worst} names={names} />
        </li>
      ))}
    </ul>
  );
}

const NOTE = "m-0 max-w-measure text-meta leading-tight text-ink-2";

export function Luck({ chapter }: { chapter: LuckChapter }) {
  const { teams, swap, example, weeks, median_games: medians } = chapter.facts;
  // The swap records hold the median games too, as the standings do.
  const games = weeks + medians;
  return (
    <ReportChapter id={chapter.key} title={chapter.title} blurb={chapter.blurb}>
      {example && <LuckCard example={example} weeks={weeks} />}
      <LuckTable teams={teams} />
      <p className={NOTE}>
        These count the {weeks} head-to-head games only.{medians > 0 && " The median game is out."} Luck is real wins
        minus wins if you played everyone.
      </p>
      <h4 className="m-0 mt-sp-3 text-body leading-tight font-bold">The Schedule Swap</h4>
      <p className="m-0 max-w-measure text-lead text-ink-2">
        Each row puts your scores against another team's schedule. Here is your best and your worst.
      </p>
      <p className={NOTE}>
        {medians > 0
          ? `These records count all ${games} games, ${weeks} head to head and ${medians} median games, as in the standings.`
          : `These records count all ${games} head-to-head games, as in the standings.`}{" "}
        Best and worst use the {Math.max(swap.best_and_worst.length - 1, 0)} other schedules.
      </p>
      <SwapRows rows={swap.best_and_worst} />
    </ReportChapter>
  );
}
