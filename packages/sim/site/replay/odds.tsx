/**
 * The odds of all runs below the replay: the playoff, bye, and title odds of each team over every run of the sim, in
 * the order of mean wins, with a column for the seed of the run on the stage. One run is never the forecast.
 */
import { thousands } from "@cpc/design/format/format";
import { cn } from "@cpc/design/lib/utils";
import { Card } from "@cpc/design/parts/card";
import type { Sim } from "../schema/sim-types";

/* The heads keep their words on one line, so a narrow column never breaks a word. */
const HEAD = "px-sp-1 py-sp-2 text-right font-mono text-meta font-bold whitespace-nowrap text-mute uppercase";
const CELL = "px-sp-1 py-sp-1 text-right font-mono text-meta tabular-nums whitespace-nowrap";

export function Odds({ sim, seeds }: { sim: Sim; seeds: Map<number, number> | null }) {
  const teams = Object.values(sim.teams).sort((a, b) => b.mean_wins - a.mean_wins || a.roster_id - b.roster_id);
  return (
    <Card className="rounded-report p-sp-3">
      <table className="w-full table-fixed border-collapse">
        <caption className="pb-sp-2 text-left font-mono text-meta font-bold tracking-caps text-accent-ink uppercase">
          {`The Odds of All ${thousands(sim.runs)} Runs`}
        </caption>
        <thead>
          <tr className="border-b border-rule">
            <th scope="col" className={cn(HEAD, "w-auto text-left")}>Team</th>
            <th scope="col" className={cn(HEAD, "w-[4.25rem]")}>Playoff</th>
            <th scope="col" className={cn(HEAD, "w-[3rem]")}>Bye</th>
            <th scope="col" className={cn(HEAD, "w-[3.5rem]")}>Title</th>
            <th scope="col" className={cn(HEAD, "w-[3rem]")}>
              <abbr title="The seed of this run" className="no-underline">Seed</abbr>
            </th>
          </tr>
        </thead>
        <tbody>
          {teams.map((team) => (
            <tr key={team.roster_id} className="border-b border-rule last:border-b-0">
              <th scope="row" className="py-sp-1 pr-sp-1 text-left text-meta leading-tight font-semibold text-ink">
                {sim.names[team.roster_id]}
              </th>
              <td className={CELL}>{`${team.playoff}%`}</td>
              <td className={CELL}>{`${team.bye}%`}</td>
              <td className={cn(CELL, "font-bold")}>{`${team.title}%`}</td>
              <td className={cn(CELL, "text-ink-2")}>{seeds?.get(team.roster_id) ?? "–"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </Card>
  );
}
