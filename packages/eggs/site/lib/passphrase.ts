/**
 * The league passphrase in local storage, under the same key as the trade analyzer, so a manager types it once per browser.
 * Every access is guarded, because a private window or blocked site data makes storage throw.
 */
// The analyzer stores the passphrase under this key too, so one entry serves the claim and the trade analyzer.
const KEY = "cpc.passphrase";

export function getPassphrase(): string | null {
  try {
    return localStorage.getItem(KEY);
  } catch {
    return null;
  }
}

export function setPassphrase(value: string): void {
  try {
    localStorage.setItem(KEY, value);
  } catch {
    // The claim still runs for this visit. The sheet asks again on the next find.
  }
}

export function clearPassphrase(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // Nothing to clear when storage is blocked.
  }
}
