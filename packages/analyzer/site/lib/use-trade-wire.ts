/**
 * The live Trade Wire: the accepted trades of Deadline week, read from the Trade Wire route each 10 s while the tab shows.
 * The Deadline banner reads it for its badge, and the sheet reads it for the list, so both show the same read.
 */
"use client";

import { useEffect, useState } from "react";
import { type ApiTarget, fetchTradeWire, type WireTrade } from "./api";
import { getPassphrase } from "./passphrase";

/* The route keeps its answer for 5 s, so a poll each 10 s shows a new trade about 5 to 15 s after Sleeper accepts it. */
export const POLL_MS = 10_000;

/* The trades are null until the first good read. A failed read keeps the last good list and sets failed, so one bad read
   never empties the list. readAt is the time of the last good read, for "Updated Ns ago". */
export type TradeWire = { trades: WireTrade[] | null; failed: boolean; readAt: number | null };

const UNREAD: TradeWire = { trades: null, failed: false, readAt: null };

/* The hook reads at once and each POLL_MS while the tab shows. It sends no call while the tab hides, so a phone in a
   pocket does no work, and it reads at once when the tab shows again. */
export function useTradeWire(api: ApiTarget): TradeWire {
  const [wire, setWire] = useState<TradeWire>(UNREAD);
  const { url, client, season } = api;

  useEffect(() => {
    let stopped = false;
    let timer: number | undefined;

    const read = async () => {
      // With no passphrase the route can only answer 401, so the site sends no call, as every other read of the site
      // does. The sheet shows the note of a failed read until the reader types the passphrase.
      const passphrase = getPassphrase();
      if (passphrase === null) {
        setWire((last) => ({ ...last, failed: true }));
        return;
      }
      try {
        const trades = await fetchTradeWire({ url, client, season }, passphrase);
        if (!stopped) setWire({ trades, failed: false, readAt: Date.now() });
      } catch {
        if (!stopped) setWire((last) => ({ ...last, failed: true }));
      }
    };

    const start = () => {
      void read();
      timer = window.setInterval(read, POLL_MS);
    };
    const stop = () => {
      window.clearInterval(timer);
      timer = undefined;
    };
    const onVisibility = () => {
      if (document.visibilityState === "hidden") stop();
      else if (timer === undefined) start();
    };

    if (document.visibilityState !== "hidden") start();
    document.addEventListener("visibilitychange", onVisibility);
    return () => {
      stopped = true;
      stop();
      document.removeEventListener("visibilitychange", onVisibility);
    };
  }, [url, client, season]);

  return wire;
}
