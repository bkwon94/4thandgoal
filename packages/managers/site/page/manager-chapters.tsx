/**
 * The five chapters of a manager page under the hero, each with its heading and its id for the chapter rail.
 * The rail and the page read one list of ids and labels, so the rail labels match the chapter headings.
 */
import type { RailChapter } from "@cpc/design/parts/chapter-rail";
import type { Manager, ManagerEntry } from "../schema/manager-types";
import { BestAdds } from "./best-adds";
import { Moves } from "./moves";
import { Roster } from "./roster";
import { SeasonSoFar } from "./season-so-far";
import { TopPerformers } from "./top-performers";

/* Each id matches the Chapter id in that chapter's component, in the order the page renders them. */
export const MANAGER_CHAPTERS: RailChapter[] = [
  { id: "season", label: "Season So Far" },
  { id: "roster", label: "Roster" },
  { id: "best-adds", label: "Best Adds" },
  { id: "top-performers", label: "Top Performers" },
  { id: "moves", label: "Moves" },
];

export function ManagerChapters({
  manager,
  managers,
  managersHref,
}: {
  manager: Manager;
  managers: ManagerEntry[];
  managersHref: string | null;
}) {
  return (
    <>
      <SeasonSoFar manager={manager} teams={managers.length} />
      <Roster manager={manager} teams={managers.length} />
      <BestAdds manager={manager} />
      <TopPerformers manager={manager} />
      <Moves manager={manager} managers={managers} managersHref={managersHref} />
    </>
  );
}
