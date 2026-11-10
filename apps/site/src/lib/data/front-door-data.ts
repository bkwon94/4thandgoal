/**
 * Reads the data of the front door at build time: the latest week, the teams of the league for the sheet of Your team,
 * and the Answers of the league Topics of each team from topics.json, each with the page that "Read the full report" opens.
 */
import { existsSync } from "node:fs";
import { join } from "node:path";
import { managerHref, managersHref, rankingsHref, weekHref } from "../routes";
import { readPublished } from "./published-file";
import { type LeagueTopic, type TopicAnswer, topicsFileSchema } from "./topics-schema";
import { listWeeks, loadWeek, type WeekRef } from "./week-data";

/* One team of the sheet. The rank and the record come from the table of the latest week. */
export type DoorTeam = { id: number; name: string; avatar: string | null; wins: number; losses: number; rank: number };

/* The Answer of one league Topic, with the page of its long form. A Topic whose page the client lacks has no link. */
export type DoorAnswer = TopicAnswer & { href: string | null };

export type FrontDoorData = {
  week: number;
  teams: DoorTeam[];
  // The league Answers of each team by roster id. A week from before the weekly build wrote topics.json has none.
  answers: Record<number, DoorAnswer[]>;
};

/* The Topics file layout version this site reads. It counts apart from the page JSON version. */
const TOPICS_VERSION = 1;

const publicFile = (...parts: string[]) => join(process.cwd(), "public", ...parts);

/* The page of each league Topic, as the table of the spec names it. A season file that the client does not publish,
   such as no rankings, gives no link. */
function hrefOf(topic: LeagueTopic, ref: WeekRef, rosterId: number): string | null {
  const week = weekHref(ref.season, ref.week);
  const managers = existsSync(publicFile(ref.season, "managers.json"));
  switch (topic) {
    case "week_recap":
      return week;
    case "last_matchup":
      return `${week}#matchups`;
    case "next_matchup":
      return `${week}#next-week`;
    case "leaders_trades":
      return `${week}#leaders`;
    case "power_rankings":
      return existsSync(publicFile(ref.season, "rankings.json")) ? rankingsHref() : null;
    case "playoff_race":
      return managers ? `${managersHref(ref.season)}#race` : null;
    case "your_season":
      return managers ? managerHref(ref.season, rosterId) : null;
  }
}

/* The data of the latest published week, or null when no week is published yet. listWeeks sorts by season, then by
   week, so the last ref is the latest. */
export function loadFrontDoor(): FrontDoorData | null {
  const ref = listWeeks().at(-1);
  if (!ref) return null;
  const page = loadWeek(ref.season, ref.week);
  // The week JSON paths are relative to the week folder, so each avatar gets the folder in front.
  const folder = `/${ref.season}/${ref.week}`;
  const teams = page.table.map(({ team, standing }) => {
    const avatar = page.avatars[String(team.roster_id)];
    return {
      id: team.roster_id,
      name: team.name,
      avatar: avatar ? `${folder}/${avatar}` : null,
      wins: standing.wins,
      losses: standing.losses,
      rank: standing.rank,
    };
  });
  // A manager looks for a name, so the sheet lists the teams by name and not by rank.
  teams.sort((a, b) => a.name.localeCompare(b.name, "en", { sensitivity: "base" }));
  const topics = readPublished(publicFile(ref.season, ref.week, "topics.json"), TOPICS_VERSION, topicsFileSchema);
  const answers: Record<number, DoorAnswer[]> = {};
  for (const [key, list] of Object.entries(topics?.teams ?? {})) {
    const rosterId = Number(key);
    answers[rosterId] = list.map((answer) => ({ ...answer, href: hrefOf(answer.topic, ref, rosterId) }));
  }
  return { week: page.week, teams, answers };
}
