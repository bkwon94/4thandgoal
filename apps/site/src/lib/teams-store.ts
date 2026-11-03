/**
 * The teams list in session storage, so the analyzer can show the pickers before the teams fetch answers.
 * A try/catch guards every access, because a private window or blocked site data makes storage throw.
 */
import { fetchTeams, type Team } from "@/lib/api";
import { season } from "@/lib/config";

// One key per season. The entry holds the time of the store, so a reader can skip an old list.
const KEY_PREFIX = "cpc.teams.";

// A roster can change after a trade, so an entry older than this counts as absent.
const MAX_AGE_MS = 5 * 60 * 1000;

type StoredTeams = { storedAt: number; teams: Team[] };

function storageKey(): string {
  return `${KEY_PREFIX}${season}`;
}

/* The stored teams for the season, or null when the entry is absent, old, or unreadable. */
export function readStoredTeams(): Team[] | null {
  try {
    const raw = sessionStorage.getItem(storageKey());
    if (!raw) return null;
    const entry = JSON.parse(raw) as StoredTeams;
    if (typeof entry?.storedAt !== "number" || !Array.isArray(entry.teams)) return null;
    if (Date.now() - entry.storedAt > MAX_AGE_MS) return null;
    return entry.teams;
  } catch {
    return null;
  }
}

export function storeTeams(teams: Team[]): void {
  try {
    const entry: StoredTeams = { storedAt: Date.now(), teams };
    sessionStorage.setItem(storageKey(), JSON.stringify(entry));
  } catch {
    // The page still works. The analyzer fetches the teams itself.
  }
}

/* Removes the entry, for a list that the API says is out of date. */
export function clearStoredTeams(): void {
  try {
    sessionStorage.removeItem(storageKey());
  } catch {
    // Nothing to clear when storage is blocked.
  }
}

/* Fetches the teams and stores the answer. A failed fetch throws the ApiError and leaves the store as it is. */
export async function fetchAndStoreTeams(passphrase: string): Promise<Team[]> {
  const teams = await fetchTeams(passphrase);
  storeTeams(teams);
  return teams;
}
