/**
 * The sim page in the playoff weeks and after the final: the card of Your team first (its game with two What-if tiles, its bye, the
 * out line, or the champion), the title odds of each team left, and the bracket, from the playoff part of the page block.
 */
"use client";

import { Trophy } from "lucide-react";
import { useId } from "react";
import { PhotoFrame } from "@cpc/design/parts/photo-frame";
import { cn } from "@cpc/design/lib/utils";
import { Toggle, ToggleGroup } from "@cpc/design/ui/toggle-group";
import type { Playoffs, SetResult, WeekSim } from "../schema/sim-types";
import { CARD, LABEL, chanceText, nameOf, oddsText, roundName, scoreText, winText } from "./format";
import { Bar } from "./parts";
import type { Avatars } from "./sim-page";
import type { Choice } from "./use-what-if";
import { TILE } from "./week-card";

type Round = Playoffs["rounds"][number];
type Game = Round["games"][number];

/* The line of Your season under the name: the seed, how the season ended, or the champion. */
export function seasonLine(playoffs: Playoffs, you: number): string {
  if (playoffs.champion === you) return "Champion";
  if (playoffs.seed === null) return "Out of the playoffs";
  if (playoffs.alive) return `Seed ${playoffs.seed}`;
  const lost = playoffs.rounds.findIndex((round) =>
    round.games.some(
      (game) => game.winner !== null && game.winner !== you && game.teams.includes(you),
    ),
  );
  return `Seed ${playoffs.seed} · Out in the ${roundName(lost, playoffs.rounds.length).toLowerCase()}`;
}

/* The What-if of the game card: the set result of the game, the title odds of the answer once it comes, and the tap. */
export type GameWhatIf = {
  chosen: SetResult | null;
  title: number | null;
  onChoose: (choice: Choice) => void;
};

/* `shown` is the playoff part that the page shows: that of the What-if answer, or the file. The game card keeps the game
   of the file, so its tiles still show the odds of each result, as a set week of the regular season does. */
export function InPlayoffs({
  sim,
  you,
  avatars,
  shown,
  whatIf,
}: {
  sim: WeekSim;
  you: number;
  avatars: Avatars;
  shown?: Playoffs;
  whatIf?: GameWhatIf;
}) {
  const file = sim.pages[you].playoffs!;
  const playoffs = shown ?? file;
  const over = playoffs.champion !== null;
  return (
    <div className="gap-sp-3 desktop:grid-cols-2 grid w-full grid-cols-1 items-start">
      {over ? (
        <ChampionCard sim={sim} playoffs={playoffs} avatars={avatars} />
      ) : file.game !== null ? (
        <GameCard sim={sim} playoffs={file} whatIf={whatIf} />
      ) : playoffs.bye ? (
        <ByeCard playoffs={playoffs} />
      ) : (
        <OutCard playoffs={playoffs} />
      )}
      {!over && <TitleOdds sim={sim} playoffs={playoffs} you={you} />}
      <Bracket sim={sim} playoffs={playoffs} you={you} />
    </div>
  );
}

/* The game of Your team in this round, with the title odds after a win and after a loss. A tap on a tile sets that
   result as a What-if, and a tap on the set tile clears it. The set tile shows the title odds of the answer, so it agrees
   with the header. */
function GameCard({
  sim,
  playoffs,
  whatIf,
}: {
  sim: WeekSim;
  playoffs: Playoffs;
  whatIf?: GameWhatIf;
}) {
  const game = playoffs.game!;
  const title = useId();
  const index = playoffs.rounds.findIndex((round) => round.week === game.week);
  const count = playoffs.rounds.length;
  const [win, loss] = game.results;
  const next =
    index === count - 1 ? "The title" : `To the ${roundName(index + 1, count).toLowerCase()}`;
  const chosen = whatIf?.chosen ?? null;
  const oddsOf = (result: typeof win) =>
    chosen?.game === result.game && whatIf?.title != null
      ? oddsText(whatIf.title)
      : oddsText(result.title, result.about);
  const choose = (value: string[]) => {
    const picked = game.results.find((result) => result.game === value[0]);
    whatIf?.onChoose(picked === undefined ? null : { game: picked.game, median: null });
  };
  return (
    <article className={CARD} aria-labelledby={title}>
      <span className={cn(LABEL, "text-mute")}>{roundName(index, count)}</span>
      <h2 id={title} className="text-lead m-0 leading-tight font-bold text-balance">
        {`Week ${game.week} vs ${nameOf(sim, game.opponent)}`}
      </h2>
      <p className="pb-sp-1 text-meta text-mute m-0 text-pretty">
        {`${winText(index, count)} ${oddsOf(win)} to win it all.`}
      </p>
      <ToggleGroup
        aria-label="Results"
        value={chosen === null ? [] : [chosen.game]}
        onValueChange={choose}
        loop
        className="gap-sp-2 grid grid-cols-2"
      >
        <PlayoffTile value="win" label="Win" odds={oddsOf(win)} chance={win.chance} note={next} />
        <PlayoffTile
          value="loss"
          label="Lose"
          odds={oddsOf(loss)}
          chance={loss.chance}
          note="Season over"
        />
      </ToggleGroup>
    </article>
  );
}

/* One result of the bracket game: the title odds after it, how likely it is, and what it leads to. It has the look and
   the press of a result tile of the regular weeks. */
function PlayoffTile({
  value,
  label,
  odds,
  chance,
  note,
}: {
  value: string;
  label: string;
  odds: string;
  chance: number;
  note: string;
}) {
  return (
    <Toggle value={value} className={TILE}>
      <span data-result-name className="text-row leading-tight font-bold">
        {label}
      </span>
      <span className="text-stat font-mono leading-none font-bold tabular-nums">{odds}</span>
      <span className="pt-sp-1 text-meta text-mute group-data-pressed:text-on-dark flex flex-col leading-tight tabular-nums">
        <span>Title odds</span>
        <span>{`${chanceText(chance)} · ${note}`}</span>
      </span>
    </Toggle>
  );
}

/* A bye: Your team plays no game this round, so no result sets yet. */
function ByeCard({ playoffs }: { playoffs: Playoffs }) {
  const title = useId();
  const week = playoffs.week!;
  return (
    <article className={CARD} aria-labelledby={title}>
      <h2 id={title} className="text-lead m-0 leading-tight font-bold">{`Bye in week ${week}`}</h2>
      <p className="text-body text-mute m-0 text-pretty">
        {`You rest this week. Your next game is in week ${week + 1}, against a winner of week ${week}.`}
      </p>
    </article>
  );
}

/* A team out of the playoffs follows the race for the title. */
function OutCard({ playoffs }: { playoffs: Playoffs }) {
  const title = useId();
  const left = playoffs.teams.filter((team) => team.alive).length;
  return (
    <article className={CARD} aria-labelledby={title}>
      <h2 id={title} className="text-lead m-0 leading-tight font-bold">
        Out of the playoffs
      </h2>
      <p className="text-body text-mute m-0 text-pretty">{`Your season is over. ${left} teams are left in the race for the title.`}</p>
    </article>
  );
}

/* After the final: the champion and the score of the final. */
function ChampionCard({
  sim,
  playoffs,
  avatars,
}: {
  sim: WeekSim;
  playoffs: Playoffs;
  avatars: Avatars;
}) {
  const title = useId();
  const champion = playoffs.champion!;
  const final = playoffs.rounds[playoffs.rounds.length - 1].games[0];
  const [a, b] = final.teams as [number, number];
  const [sa, sb] = final.scores!;
  const loser = champion === a ? b : a;
  const [won, lost] = champion === a ? [sa, sb] : [sb, sa];
  return (
    <article className={cn(CARD, "py-sp-4 items-center text-center")} aria-labelledby={title}>
      <span className="relative">
        <PhotoFrame
          src={avatars[String(champion)] ?? null}
          name={nameOf(sim, champion)}
          size="lg"
          decorative
        />
        <span className="-right-sp-1 -bottom-sp-1 size-sp-6 rounded-pill border-rule bg-card text-accent-ink absolute flex items-center justify-center border">
          <Trophy aria-hidden className="size-4" />
        </span>
      </span>
      <h2 id={title} className={cn(LABEL, "pt-sp-1 text-mute m-0")}>{`${sim.season} champion`}</h2>
      <p className="text-stat m-0 leading-tight font-bold text-balance">{nameOf(sim, champion)}</p>
      <p className="text-meta text-mute m-0 text-pretty tabular-nums">
        {`Beat ${nameOf(sim, loser)} ${scoreText(won)} to ${scoreText(lost)} in the final.`}
      </p>
    </article>
  );
}

/* The title odds of each team left, best first. */
function TitleOdds({ sim, playoffs, you }: { sim: WeekSim; playoffs: Playoffs; you: number }) {
  const title = useId();
  const left = playoffs.teams
    .filter((team) => team.alive)
    .sort((x, y) => y.title - x.title || x.seed - y.seed);
  return (
    <section className={CARD} aria-labelledby={title}>
      <h2 id={title} className="text-lead m-0 leading-tight font-bold">
        Title odds
      </h2>
      <ul className="m-0 list-none p-0">
        {left.map((team) => (
          <li
            key={team.roster_id}
            className="py-sp-2 gap-x-sp-2 border-rule grid grid-cols-[1.5rem_minmax(0,1fr)_minmax(3rem,30%)_3rem] items-center border-t first:border-t-0"
          >
            <span className="text-meta text-mute font-mono tabular-nums">{team.seed}</span>
            <span
              className={cn(
                "text-body min-w-0 leading-tight text-pretty",
                team.roster_id === you && "font-bold",
              )}
            >
              {nameOf(sim, team.roster_id)}
            </span>
            <Bar value={team.title} />
            <span className="text-body text-right font-mono font-bold tabular-nums">
              {oddsText(team.title)}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}

/* The bracket: one column per round. A played game shows its scores, an open game the title odds of each set team. */
function Bracket({ sim, playoffs, you }: { sim: WeekSim; playoffs: Playoffs; you: number }) {
  const title = useId();
  const count = playoffs.rounds.length;
  const seeds = new Map(playoffs.teams.map((team) => [team.roster_id, team]));
  return (
    <section className={cn(CARD, "desktop:col-span-2")} aria-labelledby={title}>
      <h2 id={title} className="text-lead m-0 leading-tight font-bold">
        Bracket
      </h2>
      <div className="gap-sp-3 tablet:grid-cols-3 grid grid-cols-1">
        {playoffs.rounds.map((round, index) => (
          <div key={round.week} className="gap-sp-2 flex min-w-0 flex-col">
            <h3
              className={cn(LABEL, "text-mute m-0")}
            >{`${roundName(index, count)} · Week ${round.week}`}</h3>
            {round.games.map((game, g) => (
              <BracketGame
                key={`${round.week}-${g}`}
                sim={sim}
                game={game}
                round={round}
                seeds={seeds}
                you={you}
              />
            ))}
          </div>
        ))}
      </div>
    </section>
  );
}

function BracketGame({
  sim,
  game,
  round,
  seeds,
  you,
}: {
  sim: WeekSim;
  game: Game;
  round: Round;
  seeds: Map<number, Playoffs["teams"][number]>;
  you: number;
}) {
  return (
    <ul className="rounded-report border-rule bg-page m-0 list-none overflow-hidden border p-0">
      {game.teams.map((id, side) => {
        if (id === null) {
          return (
            <li
              key={`open-${side}`}
              className="border-rule px-sp-3 py-sp-2 text-meta text-mute flex items-center border-t first:border-t-0"
            >
              {`Winner of week ${round.week - 1}`}
            </li>
          );
        }
        const team = seeds.get(id);
        const lost = game.winner !== null && game.winner !== id;
        const value =
          game.scores !== null ? scoreText(game.scores[side]) : oddsText(team?.title ?? 0);
        return (
          <li
            key={id}
            className={cn(
              "gap-sp-2 border-rule px-sp-3 py-sp-2 flex items-center border-t first:border-t-0",
              lost && "text-mute",
              // oxlint-disable-next-line design/no-arbitrary-value -- the inset accent bar marks the row of the reader, a one-off
              id === you && "shadow-[inset_3px_0_0_var(--color-accent)]",
            )}
          >
            <span className="w-sp-3 text-meta text-mute flex-none font-mono tabular-nums">
              {team?.seed}
            </span>
            <span
              className={cn(
                "text-body min-w-0 flex-1 leading-tight text-pretty",
                game.winner === id && "font-bold",
              )}
            >
              {nameOf(sim, id)}
            </span>
            <span
              className={cn(
                "text-body flex-none font-mono tabular-nums",
                game.winner === id && "font-bold",
              )}
            >
              {value}
            </span>
          </li>
        );
      })}
    </ul>
  );
}
