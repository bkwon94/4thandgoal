/**
 * The trades-open pin of `bun test`. The client build reads the clock, so a build after the Lock of cpc writes
 * tradesClosed as true. A test of a trade Topic needs the trades-open page, so it calls `pinTradesOpen` at the top level.
 * The pin sets the value of the client values before each test and puts the built value back after it.
 */
import { afterEach, beforeEach } from "bun:test";
import { clientValues } from "@/generated/client-values";

/** Make each test of the file see a client with its trades open. */
export function pinTradesOpen(): void {
  const built = clientValues.tradesClosed;
  beforeEach(() => {
    clientValues.tradesClosed = false;
  });
  afterEach(() => {
    clientValues.tradesClosed = built;
  });
}
