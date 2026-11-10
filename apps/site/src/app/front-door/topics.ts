/**
 * The 13 Topics of the front door, and the hard rules that pick the 3 Suggestions: the day of the week sets the order,
 * a Topic needs a fact to show, and an opened Topic waits until its fact changes (decision 02).
 */

/* The kind says who builds the Answer: the weekly build, the API live, or the trade judge. */
export type TopicKind = "league" | "personal" | "judgment";

export type Topic = { key: string; name: string; kind: TopicKind };

/* The order of the table of the spec. "More" lists the Topics in this order. */
export const TOPICS: readonly Topic[] = [
  { key: "week_recap", name: "Week recap", kind: "league" },
  { key: "last_matchup", name: "Your last matchup", kind: "league" },
  { key: "next_matchup", name: "Your next matchup", kind: "league" },
  { key: "power_rankings", name: "Power rankings", kind: "league" },
  { key: "playoff_race", name: "Playoff race", kind: "league" },
  { key: "your_season", name: "Your season", kind: "league" },
  { key: "leaders_trades", name: "Position leaders and recent trades", kind: "league" },
  { key: "waiver_targets", name: "Waiver targets", kind: "personal" },
  { key: "stack_up", name: "How you stack up", kind: "personal" },
  { key: "weak_spots", name: "Weak spots", kind: "personal" },
  { key: "sell_high", name: "Sell high or buy low", kind: "judgment" },
  { key: "trade_ideas", name: "Trade ideas", kind: "judgment" },
  { key: "trade_check", name: "Trade check", kind: "judgment" },
];

export const SUGGESTION_COUNT = 3;

/* The Topics that lead each day, from Sunday (0) to Saturday (6). The rest follow in the order of TOPICS.
   Why: the fantasy week has a fixed rhythm. Monday night ends the games, Tuesday is the recap, Wednesday the waivers,
   Thursday to Sunday the next game. */
const DAY_LEADS: Record<number, string[]> = {
  0: ["next_matchup", "weak_spots", "playoff_race"],
  1: ["next_matchup", "playoff_race", "power_rankings"],
  2: ["week_recap", "last_matchup", "power_rankings", "playoff_race"],
  3: ["waiver_targets", "weak_spots", "power_rankings", "week_recap", "playoff_race"],
  4: ["next_matchup", "trade_ideas", "sell_high", "weak_spots", "playoff_race"],
  5: ["next_matchup", "weak_spots", "trade_check", "playoff_race"],
  6: ["next_matchup", "weak_spots", "playoff_race"],
};

/* The keys of all 13 Topics in the order of one day of the week. */
export function dayOrder(day: number): string[] {
  const leads = DAY_LEADS[day] ?? [];
  return [...leads, ...TOPICS.map((topic) => topic.key).filter((key) => !leads.includes(key))];
}

/* The first 3 Topics of the day that have a fact, past the Topics that the manager opened at the same fact.
   A Topic with no fact yet, such as a live Topic before the API serves it, never shows as a Suggestion. */
export function pickSuggestions(day: number, facts: Record<string, string>, opened: Record<string, string>): string[] {
  return dayOrder(day)
    .filter((key) => key in facts && opened[key] !== facts[key])
    .slice(0, SUGGESTION_COUNT);
}
