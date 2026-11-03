/**
 * Fetches the teams in the background on the home page and keeps them in session storage.
 * The analyzer then shows the pickers at once. It renders nothing.
 */
"use client";

import { useEffect } from "react";
import { getPassphrase } from "@/lib/passphrase";
import { fetchAndStoreTeams } from "@/lib/teams-store";

export function TeamsPrefetch() {
  useEffect(() => {
    // With no passphrase the call gets a 401, so the component skips it.
    const passphrase = getPassphrase();
    if (!passphrase) return;
    fetchAndStoreTeams(passphrase).catch(() => {
      // The prefetch is only a head start. The analyzer fetches again and shows any error.
    });
  }, []);
  return null;
}
