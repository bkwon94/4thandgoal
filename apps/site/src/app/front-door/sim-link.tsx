/**
 * The link of the sim page for the blocks of the front door, such as the standings ladder of Playoff race.
 * The door page gives it from the Menu link of the sim, so a client or a season with no sim page has no link.
 */
"use client";

import { createContext, useContext, type ReactNode } from "react";

const SimLink = createContext<string | null>(null);

export function SimLinkProvider({ href, children }: { href: string | null; children: ReactNode }) {
  return <SimLink.Provider value={href}>{children}</SimLink.Provider>;
}

/* The path of the sim page, such as "/sim/2026/", or null with no sim page. */
export const useSimLink = (): string | null => useContext(SimLink);
