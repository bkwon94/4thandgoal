/**
 * The rules of an Announcement: it opens once per browser, on page load, never over another sheet, never on the page it
 * links to, and never on or after its stop date. A dismiss or a press of its link keeps it hidden in local storage.
 */
"use client";

import { useCallback, useEffect, useState } from "react";

/* The page settles first, so a sheet that the page opens on load, such as the team sheet, shows before the check. */
export const LOAD_BEAT_MS = 700;

/* The seen key of each Announcement starts with this prefix and ends with its id. */
export const ANNOUNCEMENT_KEY_PREFIX = "cpc.announcement.";

const keyOf = (id: string) => `${ANNOUNCEMENT_KEY_PREFIX}${id}`;

/* Every access is guarded, because a private window or blocked site data makes storage throw. Blocked storage reads as
   not seen, so the Announcement can show on each load there. */
function seen(id: string): boolean {
  try {
    return localStorage.getItem(keyOf(id)) === "seen";
  } catch {
    return false;
  }
}

function markSeen(id: string): void {
  try {
    localStorage.setItem(keyOf(id), "seen");
  } catch {
    // The Announcement still closes for this visit.
  }
}

/* The local date as YYYY-MM-DD, so a stop date holds to the calendar day of the manager. */
function today(): string {
  const now = new Date();
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`;
}

/* An open sheet or dialog of the site marks itself aria-modal: the shared Sheet, the Dialog, and the team sheet. */
function anotherSheetOpen(): boolean {
  return document.querySelector('[aria-modal="true"]') !== null;
}

/* `read` gives the data that the use needs, or null when it cannot open on this load, such as with no team set. A load
   that skips the open for any reason does not count as seen, so it shows on the next load. `data` stays after a close, so
   the sheet keeps its content while it leaves. */
export function useAnnouncement<T>({ id, href, stops, read }: { id: string; href: string; stops: string; read: () => T | null }) {
  const [open, setOpen] = useState(false);
  const [data, setData] = useState<T | null>(null);

  useEffect(() => {
    if (seen(id) || today() >= stops || window.location.pathname.startsWith(href)) return;
    const timer = window.setTimeout(() => {
      if (anotherSheetOpen()) return;
      const next = read();
      if (next === null) return;
      setData(next);
      setOpen(true);
    }, LOAD_BEAT_MS);
    return () => window.clearTimeout(timer);
    // The check runs once per page load. A new `read` on a render of the parent does not start it again.
  }, [id, href, stops]);

  // Any close counts as seen: "Not now", Escape, a tap on the dim, or a drag down.
  const dismiss = useCallback(() => {
    markSeen(id);
    setOpen(false);
  }, [id]);

  // A press of the link counts as seen too. The browser then follows the link.
  const follow = useCallback(() => markSeen(id), [id]);

  return { open, data, dismiss, follow };
}
