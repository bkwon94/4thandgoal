/**
 * The league passphrase in local storage, so a manager types it once per phone.
 * Every access is guarded, because a private window or blocked site data makes storage throw.
 */
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
    // The page still works for this visit. The dialog asks again on the next load.
  }
}

export function clearPassphrase(): void {
  try {
    localStorage.removeItem(KEY);
  } catch {
    // Nothing to clear when storage is blocked.
  }
}
