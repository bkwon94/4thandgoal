/**
 * The hide state of the egg banner in local storage, keyed by drop, as a convenience of one viewer.
 * Every access is guarded, because a private window or blocked site data makes storage throw.
 */
// The key holds the drop that the viewer hid. A newer drop has another value, so the banner shows again.
const KEY = "cpc.eggs.banner-hidden";

/* The one name of a drop: its week and its time. A drop of one week happens once, so the pair never repeats. */
export function dropKey(drop: { week: number; dropped_at: string }): string {
  return `${drop.week}@${drop.dropped_at}`;
}

export function isBannerHidden(drop: string): boolean {
  try {
    return localStorage.getItem(KEY) === drop;
  } catch {
    return false;
  }
}

export function hideBanner(drop: string): void {
  try {
    localStorage.setItem(KEY, drop);
  } catch {
    // The banner still hides for this visit. It shows again on the next visit.
  }
}
