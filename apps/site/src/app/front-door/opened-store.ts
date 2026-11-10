/**
 * The Topics that the manager opened, kept in local storage next to Your team: each team keeps the fact of each opened
 * Topic for one week. A new fact or a new week brings the Topic back to the Suggestions (decision 02).
 */
export const OPENED_KEY = "cpc.opened-topics";

type Opened = Record<string, { week: number; topics: Record<string, string> }>;

function readAll(): Opened {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(OPENED_KEY) ?? "{}");
    return parsed && typeof parsed === "object" && !Array.isArray(parsed) ? (parsed as Opened) : {};
  } catch {
    // Blocked storage or a bad value reads as no opened Topic.
    return {};
  }
}

/* The opened Topics of one team in this week, each with the fact it had at the open. An older week reads as none. */
export function getOpened(teamId: number, week: number): Record<string, string> {
  const entry = readAll()[String(teamId)];
  return entry && entry.week === week && entry.topics && typeof entry.topics === "object" ? entry.topics : {};
}

export function markOpened(teamId: number, week: number, topic: string, fact: string): Record<string, string> {
  const all = readAll();
  const topics = { ...getOpened(teamId, week), [topic]: fact };
  all[String(teamId)] = { week, topics };
  try {
    localStorage.setItem(OPENED_KEY, JSON.stringify(all));
  } catch {
    // The page still drops the Topic for this visit. The next load shows it again.
  }
  return topics;
}
