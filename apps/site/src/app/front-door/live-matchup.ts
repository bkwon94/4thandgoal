/**
 * The live card of Your next matchup: the API reads the live Sleeper week and sends one matchup card on its stream, with
 * the projected totals, the win odds, and the time of the read. The rest of the Topic still comes from topics.json.
 */
import { useEffect, useState } from "react";
import { type MatchupBlock, matchupBlockSchema } from "@/lib/data/blocks/matchup-schema";
import { type AskTarget, postClient } from "./ask-api";

/* The key of the one league Topic whose card the API builds live. */
export const LIVE_MATCHUP_TOPIC = "next_matchup";

/* The matchup card of the text of an API stream, or null when the stream has no card, such as for a team with no game
   in the live week. */
export function liveMatchupOf(text: string): MatchupBlock | null {
  for (const line of text.split("\n")) {
    if (!line.startsWith("data: ") || line === "data: [DONE]") continue;
    const part = JSON.parse(line.slice("data: ".length)) as { type?: string; data?: unknown };
    if (part.type !== "data-block") continue;
    const parsed = matchupBlockSchema.safeParse(part.data);
    if (parsed.success) return parsed.data;
  }
  return null;
}

/* The live card of the team of `rosterId`, or null when the API sends none. A failed call throws an AskError. */
export async function fetchLiveMatchup(target: AskTarget, passphrase: string, rosterId: number): Promise<MatchupBlock | null> {
  const response = await postClient(target, passphrase, "next-matchup", { roster_id: rosterId });
  return liveMatchupOf(await response.text());
}

/* The quiet line under the live card that says when the API read the projections. `timeZone` is the zone of the
   browser by default; a test gives one, so its line never depends on the machine. */
export function readTimeLine(readAt: string, timeZone?: string): string {
  const time = new Intl.DateTimeFormat("en-US", { hour: "numeric", minute: "2-digit", timeZone }).format(new Date(readAt));
  return `Live projections as of ${time}`;
}

/* Where the live card comes from: the API, and the league passphrase that the browser keeps. The passphrase is read at
   the call, so a passphrase typed after the Thread loaded still counts. */
export type LiveSource = { target: AskTarget; passphrase: () => string | null };

/* The live card of the team of `rosterId` for an Answer of `topic`, or null until it comes. Only Your next matchup has
   one. With no passphrase, or on a failed call, it stays null, so the card of the weekly build stays in place. */
export function useLiveMatchup(source: LiveSource | undefined, topic: string, rosterId: number): MatchupBlock | null {
  const [card, setCard] = useState<MatchupBlock | null>(null);
  useEffect(() => {
    const passphrase = source?.passphrase();
    if (!source || !passphrase || topic !== LIVE_MATCHUP_TOPIC) return;
    let current = true;
    fetchLiveMatchup(source.target, passphrase, rosterId)
      .then((block) => current && setCard(block))
      .catch(() => undefined);
    return () => {
      current = false;
    };
  }, [source, topic, rosterId]);
  return card;
}
