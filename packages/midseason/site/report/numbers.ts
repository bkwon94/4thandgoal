/**
 * The number formats of the midseason report: a full record with its ties, a signed count with one or two decimals, and a team score.
 * Each part of the report takes them from here, so each chapter writes a record, a luck, and a score the same way.
 */
import { oneDecimal, record } from "@cpc/design/format/format";

/* A record with its ties only when the team has one: "11-5" or "10-5-1". */
export const fullRecord = (wins: number, losses: number, ties: number) =>
  ties > 0 ? `${record(wins, losses)}-${ties}` : record(wins, losses);

/* A signed count with one decimal, such as a Schedule luck of "+1.5" or "−2.3". The minus is U+2212, as in gap(). */
export const signedOne = (x: number) => (x >= 0 ? `+${oneDecimal(x)}` : `−${oneDecimal(-x)}`);

/* A signed count with 2 decimals, such as a Schedule luck of "+2.73" or "−1.00" in the luck table (decision ticket 16). */
export const signedTwo = (x: number) => (x >= 0 ? `+${teamScore(x)}` : `−${teamScore(-x)}`);

/* A team score with 2 decimals, as Sleeper shows it: "158.96" and "898.00" (decision ticket 15). Player points take
   oneDecimal. The round comes first, because toFixed alone rounds by the binary value. */
export const teamScore = (x: number) => (Math.round(x * 100) / 100).toFixed(2);
