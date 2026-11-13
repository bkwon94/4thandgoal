/**
 * The 14 Topics of the front door, and the hard rules that pick the 3 Suggestions: the day of the week sets the order,
 * a Topic needs a fact to show, and an opened Topic waits until its fact changes (decision 02).
 */

/* The kind says who builds the Answer: the weekly build, the API live, or the trade judge. */
export type TopicKind = "league" | "personal" | "judgment";

/* The chip is the short name on a Suggestion chip. A whole name makes a wide chip, so a chip shows one or two words
   and the row scrolls sideways less. The full name shows in "More", in the strip, in the question, and to a screen
   reader (decision 02). */
export type Topic = { key: string; name: string; chip: string; kind: TopicKind };

/* The order of the table of the spec. "More" lists the Topics in this order. */
export const TOPICS: readonly Topic[] = [
  { key: "week_recap", name: "Week recap", chip: "Recap", kind: "league" },
  { key: "last_matchup", name: "Your last matchup", chip: "Result", kind: "league" },
  { key: "next_matchup", name: "Your next matchup", chip: "Next game", kind: "league" },
  { key: "power_rankings", name: "Power rankings", chip: "Ranks", kind: "league" },
  { key: "playoff_race", name: "Playoff race", chip: "Playoffs", kind: "league" },
  { key: "your_season", name: "Your season", chip: "Season", kind: "league" },
  { key: "leaders_trades", name: "Position leaders and recent trades", chip: "Leaders", kind: "league" },
  { key: "waiver_targets", name: "Waiver targets", chip: "Waivers", kind: "personal" },
  { key: "stack_up", name: "How you stack up", chip: "Roster", kind: "personal" },
  { key: "weak_spots", name: "Weak spots", chip: "Holes", kind: "personal" },
  { key: "start_sit", name: "Start or sit", chip: "Start/sit", kind: "personal" },
  { key: "sell_high", name: "Sell high or buy low", chip: "Sell high", kind: "judgment" },
  { key: "trade_ideas", name: "Trade ideas", chip: "Trades", kind: "judgment" },
  { key: "trade_check", name: "Trade check", chip: "Check", kind: "judgment" },
];

/* The name of a Topic by its key. A key of no known Topic shows as itself, so a new Topic of the API still reads. */
export function topicName(key: string): string {
  return TOPICS.find((topic) => topic.key === key)?.name ?? key;
}

export const SUGGESTION_COUNT = 3;

/* The Topics that lead each day, from Sunday (0) to Saturday (6). The rest follow in the order of TOPICS.
   Why: the fantasy week has a fixed rhythm. Monday night ends the games, Tuesday is the recap, Wednesday the waivers,
   Thursday to Sunday the next game. Start or sit leads the game days, and sits third on Wednesday, after the claims.
   The trade check has no weekly fact, so it leads no day and stays in "More". */
const DAY_LEADS: Record<number, string[]> = {
  0: ["start_sit", "next_matchup", "weak_spots", "playoff_race"],
  1: ["next_matchup", "playoff_race", "power_rankings"],
  2: ["week_recap", "last_matchup", "power_rankings", "playoff_race"],
  3: ["waiver_targets", "weak_spots", "start_sit", "power_rankings", "week_recap", "playoff_race"],
  4: ["start_sit", "next_matchup", "trade_ideas", "sell_high", "weak_spots", "playoff_race"],
  5: ["start_sit", "next_matchup", "weak_spots", "playoff_race"],
  6: ["start_sit", "next_matchup", "weak_spots", "playoff_race"],
};

/* The keys of all 14 Topics in the order of one day of the week. */
export function dayOrder(day: number): string[] {
  const leads = DAY_LEADS[day] ?? [];
  return [...leads, ...TOPICS.map((topic) => topic.key).filter((key) => !leads.includes(key))];
}

/* The first 3 Topics that have a fact, past the Topics that the manager opened at the same fact. The urgent Topics
   lead, most urgent first, then the order of the day. Jev judges what is urgent on the API, and this rule only places
   it. A Topic with no fact yet, such as a live Topic before the API serves it, never shows as a Suggestion. The API
   picks the head start with the same rule, in suggestions.py. */
export function pickSuggestions(day: number, facts: Record<string, string>, opened: Record<string, string>, urgent: string[] = []): string[] {
  return [...urgent, ...dayOrder(day).filter((key) => !urgent.includes(key))]
    .filter((key) => key in facts && opened[key] !== facts[key])
    .slice(0, SUGGESTION_COUNT);
}
