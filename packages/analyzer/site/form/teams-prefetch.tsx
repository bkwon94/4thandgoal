/**
 * Fetches the teams in the background on the home page and keeps them in session storage.
 * The analyzer then shows the pickers at once. It renders nothing.
 */
"use client";

import { useEffect } from "react";
import type { ApiTarget } from "../lib/api";
import { getPassphrase } from "../lib/passphrase";
import { fetchAndStoreTeams } from "../lib/teams-store";

/* The page gives the target from its config, so the part reads no env. */
export function TeamsPrefetch({ target }: { target: ApiTarget }) {
  useEffect(() => {
    // With no passphrase the call gets a 401, so the component skips it.
    const passphrase = getPassphrase();
    if (!passphrase) return;
    fetchAndStoreTeams(target, passphrase).catch(() => {
      // The prefetch is only a head start. The analyzer fetches again and shows any error.
    });
  }, [target]);
  return null;
}
