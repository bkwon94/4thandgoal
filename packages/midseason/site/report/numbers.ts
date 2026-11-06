/**
 * The number formats of the midseason report: a full record with its ties, and a signed count with one decimal.
 * Each part of the report takes them from here, so each chapter writes a record and a luck the same way.
 */
import { oneDecimal, record } from "@cpc/design/format/format";

/* A record with its ties only when the team has one: "11-5" or "10-5-1". */
export const fullRecord = (wins: number, losses: number, ties: number) =>
  ties > 0 ? `${record(wins, losses)}-${ties}` : record(wins, losses);

/* A signed count with one decimal, such as a Schedule luck of "+1.5" or "−2.3". The minus is U+2212, as in gap(). */
export const signedOne = (x: number) => (x >= 0 ? `+${oneDecimal(x)}` : `−${oneDecimal(-x)}`);
