/**
 * Reads the data of the front door at build time: the latest week, the teams of the league for the sheet of Your team,
 * and the Answers of the league Topics of each team from topics.json, each with the page that "Read the full report" opens.
 */
import { existsSync } from "node:fs";
import { gameId } from "@cpc/week/chapters/next-week";
import { join } from "node:path";
import { clientValues } from "../../generated/client-values";
import { managerHref, managersHref, rankingsHref, waiverHref, weekHref } from "../routes";
import { readPublished } from "./published-file";
import { type LeagueTopic, type TopicAnswer, topicsFileSchema } from "./topics-schema";
import type { WeekPage } from "@cpc/week/schema/week-types";
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
  // The page of each personal Topic of each team by roster id, or null when the client lacks that page.
  personalHrefs: Record<number, Record<PersonalTopic, string | null>>;
};

/* The 3 personal Topics, which the API answers live. Their pages come from the build, as the league Topics do. */
type PersonalTopic = "weak_spots" | "stack_up" | "waiver_targets";

/* The Topics file layout versions this site reads. They count apart from the page JSON version. Version 2 adds the
   block of an Answer, and a week built before it still reads as version 1, with no block. */
const TOPICS_VERSIONS = [1, 2] as const;

const publicFile = (...parts: string[]) => join(process.cwd(), "public", ...parts);

/* The id of the game of one team in the weekly report: its game of this week, or of next week. A team with no game in
   the report, such as on a bye, gets the id of the chapter. */
function gameOf(page: WeekPage, rosterId: number, when: "last" | "next"): string {
  if (when === "last") {
    const game = page.matchups.find((matchup) => matchup.sides.some((side) => side.team.roster_id === rosterId));
    return game ? gameId("last", game.sides[0].team.roster_id, game.sides[1].team.roster_id) : "matchups";
  }
  const game = page.next.find((next) => next.a.roster_id === rosterId || next.b.roster_id === rosterId);
  return game ? gameId("next", game.a.roster_id, game.b.roster_id) : "next-week";
}

/* The page of each league Topic, as the table of the spec names it. A matchup Topic links to the game of the team in the
   weekly report. A season file that the client does not publish, such as no rankings, gives no link. */
function hrefOf(topic: LeagueTopic, ref: WeekRef, page: WeekPage, rosterId: number): string | null {
  const week = weekHref(ref.season, ref.week);
  const managers = existsSync(publicFile(ref.season, "managers.json"));
  switch (topic) {
    case "week_recap":
      return week;
    case "last_matchup":
      return `${week}#${gameOf(page, rosterId, "last")}`;
    case "next_matchup":
      return `${week}#${gameOf(page, rosterId, "next")}`;
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

/* The page of each personal Topic, as the table of the spec names it. Waiver targets link to the waiver page of the week
   only when the client takes the waiver package and publishes its waiver file, and the other two link to the manager page
   of the team only when the client takes the managers package. A client that omits a package has no route for it, even
   with its file in the published data, so a link would give a 404. */
function personalHrefsOf(ref: WeekRef, rosterId: number): Record<PersonalTopic, string | null> {
  const hasManagers = clientValues.packages.includes("managers") && existsSync(publicFile(ref.season, "managers.json"));
  const hasWaiver = clientValues.packages.includes("waiver") && existsSync(publicFile(ref.season, ref.week, "waiver.json"));
  const manager = hasManagers ? managerHref(ref.season, rosterId) : null;
  const waiver = hasWaiver ? waiverHref(ref.season, ref.week) : null;
  return { weak_spots: manager, stack_up: manager, waiver_targets: waiver };
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
  const topics = readPublished(publicFile(ref.season, ref.week, "topics.json"), TOPICS_VERSIONS, topicsFileSchema);
  const answers: Record<number, DoorAnswer[]> = {};
  for (const [key, list] of Object.entries(topics?.teams ?? {})) {
    const rosterId = Number(key);
    answers[rosterId] = list.map((answer) => ({ ...answer, href: hrefOf(answer.topic, ref, page, rosterId) }));
  }
  const personalHrefs = Object.fromEntries(teams.map((team) => [team.id, personalHrefsOf(ref, team.id)]));
  return { week: page.week, teams, answers, personalHrefs };
}
